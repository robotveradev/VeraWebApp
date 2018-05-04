pragma solidity ^0.4.11;

library SafeMath {
  function mul(uint256 a, uint256 b) internal pure returns (uint256) {
    if (a == 0) {
      return 0;
    }
    uint256 c = a * b;
    assert(c / a == b);
    return c;
  }

  function div(uint256 a, uint256 b) internal pure returns (uint256) {
    // assert(b > 0); // Solidity automatically throws when dividing by 0
    uint256 c = a / b;
    // assert(a == b * c + a % b); // There is no case in which this doesn't hold
    return c;
  }

  function sub(uint256 a, uint256 b) internal pure returns (uint256) {
    assert(b <= a);
    return a - b;
  }

  function add(uint256 a, uint256 b) internal pure returns (uint256) {
    uint256 c = a + b;
    assert(c >= a);
    return c;
  }
}

contract Ownable {
     mapping(address => bool) public owners;

    function Ownable() public {
        owners[msg.sender] = true;
    }

    modifier onlyOwner() {
        require(owners[msg.sender]);
        _;
    }

    function newOwner(address _newOwner) public onlyOwner {
        if (_newOwner != address(0)) {
            owners[_newOwner] = true;
        }
    }
}


contract Oracle is Ownable {
    using SafeMath for uint256;

    bytes32 public name;
    address public beneficiary;
    ERC20 token;

    address[] employers;

    address[] candidates;

    uint8 public service_fee;

    uint256 public pipeline_max_length;

    struct Pipeline {
        uint256 id;
        bytes32 title;
        uint256 fee;
        bool approvable;
    }

    struct Vacancy {
        address keeper;
        bool paused;
        uint allowed;
    }

    struct CV {
        address keeper;
        bool paused;
    }

    // vacancy uuid => vacancy
    mapping (bytes32 => Vacancy) public vacancies;

    // Vacancy uuid => vacancy pipeline
    mapping (bytes32 => Pipeline[]) public vacancy_pipeline;

    // vacancy uuid => cvs, subscribed to vacancy
    mapping (bytes32 => bytes32[]) public cvs_on_vacancy;

    // employer address => employer vacancies list
    mapping (address => bytes32[]) vacancy_uuids;

    // cv uuid => CV
    mapping (bytes32 => CV) public cvs;

    // candidate address => candidate cvs list
    mapping (address => bytes32[]) cv_uuids;

    // cv uuid => vacancies, cv subscribed to
    mapping (bytes32 => bytes32[]) public vacancies_on_cv;

    // vacancy uuid => cv uuid => current pipeline action for cv
    mapping (bytes32 => mapping (bytes32 => Pipeline)) public current_action;

    // vacancy passed by cv
    mapping (bytes32 => mapping (bytes32 => bool)) public vacancy_pass;

    // cv requests for refresh vacancy_pass
    mapping (bytes32 => mapping (bytes32 => bool)) public cv_requests;

    struct Fact {
        address from;
        uint256 time;
        string fact;
    }

    struct Fact_dict {
        mapping(bytes32 => Fact) dict;
        bytes32[] keys;
    }

    mapping (address => Fact_dict) facts;

    // events
    event NewEmployer(address employer_address);
    event NewCandidate(address candidate_address);
    event NewVacancy(address employer_address, bytes32 id);
    event NewCV(address candidate_address, bytes32 id);
    event NewPipelineMaxLength(address sender, uint256 count);
    event NewFact(address sender, bytes32 id);
    event CVRevoked(bytes32 vacancy, bytes32 cv, address revoked_by);

    modifier onlyEmployer(bytes32 _uuid) {
        require(vacancies[_uuid].keeper == msg.sender || Ownable(vacancies[_uuid].keeper).owners(msg.sender));
        _;
    }

    modifier onlyCandidate(bytes32 _uuid) {
        require(cvs[_uuid].keeper == msg.sender|| Ownable(cvs[_uuid].keeper).owners(msg.sender));
        _;
    }

    modifier onlyRequested(bytes32 _vac, bytes32 _cv) {
        require(cv_requests[_vac][_cv]);
        _;
    }

    //"VeraOracle",5,"0x10f8e8181bb01583650d3b5c5b963da1e7d22797","0x25e802ea622fb7d850b588c0cf277981ec338325"
    function Oracle(bytes32 _name, uint8 _service_fee, address _beneficiary, address _token) public {
        name = _name;
        service_fee = _service_fee;
        beneficiary = _beneficiary;
        token = ERC20(_token);
        pipeline_max_length = 6;
    }

    function new_fact(address _candidate, string _fact) public onlyOwner {
        bytes32 _id = keccak256(_fact);
        facts[_candidate].dict[_id] = Fact(msg.sender, now, _fact);
        facts[_candidate].keys.push(_id);
        NewFact(msg.sender, _id);
    }

    function keys_of_facts_length(address _candidate) public view returns (uint) {
        return facts[_candidate].keys.length;
    }

    function keys_of_facts(address _candidate) public view returns (bytes32[]) {
        return facts[_candidate].keys;
    }

    function fact_key_by_id(address _candidate, uint256 _index) public view returns (bytes32) {
        return facts[_candidate].keys[_index];
    }

    function get_fact(address _candidate, bytes32 _id) public view returns (address from, uint256 time, string fact) {
        return (facts[_candidate].dict[_id].from, facts[_candidate].dict[_id].time, facts[_candidate].dict[_id].fact);
    }

    function new_pipeline_max_length(uint256 _new_max) public onlyOwner {
        pipeline_max_length = _new_max;
        NewPipelineMaxLength(msg.sender, _new_max);
    }

    // percent awarded for test passed by candidate
    function new_service_fee(uint8 _service_fee) public onlyOwner {
        service_fee = _service_fee;
    }

    function new_beneficiary(address _beneficiary) public onlyOwner {
        beneficiary = _beneficiary;
    }

    function new_employer(address _employer) public onlyOwner {
        employers.push(_employer);
        NewEmployer(_employer);
    }

    function get_employers() public view returns (address[]) {
        return employers;
    }

    function new_candidate(address _candidate) public onlyOwner {
        candidates.push(_candidate);
        NewCandidate(_candidate);
    }

    function get_candidates() public view returns (address[]) {
        return candidates;
    }

    // 0xdd870fa1b7c4700f2bd7f44238821c26f7392148, "vac",1000, ["first","second","exam"],[0,0,10],[true,true,true]
    function new_vacancy(address _employer_address, bytes32 _uuid, uint _allowed, bytes32[] _titles, uint256[] _fees, bool[] _approvable) public onlyOwner {
        require(_titles.length <= pipeline_max_length);
        vacancies[_uuid].allowed = _allowed;
        vacancies[_uuid].keeper = _employer_address;
        for (uint256 i=0; i < _titles.length; i++) {
            vacancy_pipeline[_uuid].push(Pipeline(i, _titles[i], _fees[i], _approvable[i]));
        }
        vacancy_uuids[_employer_address].push(_uuid);
        NewVacancy(_employer_address, _uuid);
    }


    // "0x14723a09acff6d2a60dcdf7aa4aff308fddc160c", "cv"
    function new_cv(address _candidate_address, bytes32 _uuid) public onlyOwner {
        cvs[_uuid].keeper = _candidate_address;
        cv_uuids[_candidate_address].push(_uuid);
        NewCV(_candidate_address, _uuid);
    }

    function vacancies_length(address _employer_address) public view returns (uint) {
        return vacancy_uuids[_employer_address].length;
    }

    function cvs_length(address _candidate_address) public view returns (uint) {
        return cv_uuids[_candidate_address].length;
    }

    function vacancies_on_cv_length(bytes32 _cv_uuid) public view returns (uint) {
        return vacancies_on_cv[_cv_uuid].length;
    }

    function cvs_on_vacancy_length(bytes32 _vac_uuid) public view returns (uint) {
        return cvs_on_vacancy[_vac_uuid].length;
    }

    function employer_vacancies(address _employer_address) public view returns (bytes32[]) {
        return vacancy_uuids[_employer_address];
    }

    function candidate_cvs(address _candidate_address) public view returns (bytes32[]) {
        return cv_uuids[_candidate_address];
    }


    function employer_vacancy_by_id(address _employer_address, uint256 _index) public view returns (bytes32) {
        return vacancy_uuids[_employer_address][_index];
    }

    function candidate_cv_by_id(address _candidate_address, uint256 _index) public view returns (bytes32) {
        return cv_uuids[_candidate_address][_index];
    }


    function get_vacancy_pipeline_length(bytes32 _uuid) public view returns (uint256) {
        return vacancy_pipeline[_uuid].length;
    }

    function pause_vac(bytes32 _uuid) public onlyEmployer(_uuid) {
        vacancies[_uuid].paused = true;
    }

    function unpause_vac(bytes32 _uuid) public onlyEmployer(_uuid) {
        vacancies[_uuid].paused = false;
    }

    function pause_cv(bytes32 _uuid) public onlyCandidate(_uuid) {
        cvs[_uuid].paused = true;
    }

    function unpause_cv(bytes32 _uuid) public onlyCandidate(_uuid) {
        cvs[_uuid].paused = false;
    }

    function subscribe(bytes32 _vac, bytes32 _cv) public onlyCandidate(_cv) {
        require (current_action[_vac][_cv].title == bytes32(0));
        vacancies_on_cv[_cv].push(_vac);
        cvs_on_vacancy[_vac].push(_cv);
        current_action[_vac][_cv] = vacancy_pipeline[_vac][0];
    }

    function process_action(bytes32 _vac, bytes32 _cv) private {
        require(!vacancy_pass[_vac][_cv]);
        require(!vacancies[_vac].paused);
        if (current_action[_vac][_cv].fee > 0) {
            require(vacancies[_vac].allowed >= current_action[_vac][_cv].fee);
            uint256 service_amount = current_action[_vac][_cv].fee.div(100).mul(service_fee);
            uint256 candidate_amount = current_action[_vac][_cv].fee.sub(service_amount);
            token.transferFrom(vacancies[_vac].keeper, beneficiary, service_amount);
            token.transferFrom(vacancies[_vac].keeper, cvs[_cv].keeper, candidate_amount);
            vacancies[_vac].allowed = vacancies[_vac].allowed.sub(current_action[_vac][_cv].fee);
        }
        if (vacancy_pipeline[_vac].length-2 == current_action[_vac][_cv].id) {
            vacancy_pass[_vac][_cv] = true;
        }
        current_action[_vac][_cv] = vacancy_pipeline[_vac][current_action[_vac][_cv].id+1];
    }

    function level_up(bytes32 _vac, bytes32 _cv) public onlyOwner {
        require(!current_action[_vac][_cv].approvable);
        process_action(_vac, _cv);
    }

    function approve_level_up(bytes32 _vac, bytes32 _cv) public onlyEmployer(_vac) {
        process_action(_vac, _cv);
    }

    function reset_cv(bytes32 _vac, bytes32 _cv) public onlyEmployer(_vac) {
        current_action[_vac][_cv] = Pipeline(0, '', 0, false);
        removeByValue(_vac, _cv);
        CVRevoked(_vac, _cv, msg.sender);
    }

    function removeByValue(bytes32 _vac_uuid, bytes32 _cv_uuid) private {
        uint i = find(_vac_uuid, _cv_uuid);
        removeByIndex(_vac_uuid, i);
    }

    function find(bytes32 _vac_uuid, bytes32 _cv_uuid) private view returns(uint) {
        uint i = 0;
        while (cvs_on_vacancy[_vac_uuid][i] != _cv_uuid) {
            i++;
        }
        return i;
    }

    function removeByIndex(bytes32 _vac_uuid, uint i) private {
        while (i<cvs_on_vacancy[_vac_uuid].length-1) {
            cvs_on_vacancy[_vac_uuid][i] = cvs_on_vacancy[_vac_uuid][i+1];
            i++;
        }
        cvs_on_vacancy[_vac_uuid].length--;
    }
}

contract ERC20Basic {
  uint256 public totalSupply;
  function balanceOf(address who) public view returns (uint256);
  function transfer(address to, uint256 value) public returns (bool);
  event Transfer(address indexed from, address indexed to, uint256 value);
}

contract ERC20 is ERC20Basic {
  function allowance(address owner, address spender) public view returns (uint256);
  function transferFrom(address from, address to, uint256 value) public returns (bool);
  function approve(address spender, uint256 value) public returns (bool);
  event Approval(address indexed owner, address indexed spender, uint256 value);
}

contract MultiOwnable {
    mapping (address => bool) public owners;

    event OwnerAdded(address indexed by, address indexed owner);
    event OwnerRemoved(address indexed by, address indexed owner);

    function MultiOwnable() public {
        owners[msg.sender] = true;
    }

    modifier onlyOwner() {
        require(owners[msg.sender]);
        _;
    }

    function addOwner(address newOwner) public onlyOwner {
        require(newOwner != address(0));
        owners[newOwner] = true;
        OwnerAdded(msg.sender, newOwner);
    }
}

contract Withdrawable is MultiOwnable {
    function withdraw(address _token, address _to, uint256 _amount) public onlyOwner {
        ERC20(_token).transfer(_to, _amount);
    }
}

contract Employer is Withdrawable {

    bytes32 public id;
    ERC20 token;
    Oracle oracle;

    function Employer(bytes32 _id, address _token, address _oracle) public {
        id = _id;
        token = ERC20(_token);
        oracle = Oracle(_oracle);
    }

    function approve_money(uint256 _amount) public onlyOwner {
        token.approve(oracle, _amount);
    }

    function pause_vac(bytes32 _uuid) public onlyOwner {
        oracle.pause_vac(_uuid);
    }

    function unpause_vac(bytes32 _uuid) public onlyOwner {
        oracle.unpause_vac(_uuid);
    }

    function approve_level_up(bytes32 _vac, bytes32 _cv) public onlyOwner {
        oracle.approve_level_up(_vac, _cv);
    }
    function reset_cv(bytes32 _vac, bytes32 _cv) public onlyOwner {
        oracle.reset_cv(_vac, _cv);
    }
}
