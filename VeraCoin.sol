pragma solidity ^0.4.11;


/**
 * @title SafeMath
 * @dev Math operations with safety checks that throw on error
 */
library SafeMath {
    function mul(uint256 a, uint256 b) internal constant returns (uint256) {
        uint256 c = a * b;
        assert(a == 0 || c / a == b);
        return c;
    }

    function div(uint256 a, uint256 b) internal constant returns (uint256) {
        // assert(b > 0); // Solidity automatically throws when dividing by 0
        uint256 c = a / b;
        // assert(a == b * c + a % b); // There is no case in which this doesn't hold
        return c;
    }

    function sub(uint256 a, uint256 b) internal constant returns (uint256) {
        assert(b <= a);
        return a - b;
    }

    function add(uint256 a, uint256 b) internal constant returns (uint256) {
        uint256 c = a + b;
        assert(c >= a);
        return c;
    }
}


/**
 * @title Ownable
 * @dev The Ownable contract has an owner address, and provides basic authorization control
 * functions, this simplifies the implementation of "user permissions".
 */
contract Ownable {
    address public owner;


    /**
     * @dev The Ownable constructor sets the original `owner` of the contract to the sender
     * account.
     */
    function Ownable() {
        owner = msg.sender;
    }


    /**
     * @dev Throws if called by any account other than the owner.
     */
    modifier onlyOwner() {
        require(msg.sender == owner);
        _;
    }


    /**
     * @dev Allows the current owner to transfer control of the contract to a newOwner.
     * @param newOwner The address to transfer ownership to.
     */
    function transferOwnership(address newOwner) onlyOwner {
        if (newOwner != address(0)) {
            owner = newOwner;
        }
    }

}


/*
 * Haltable
 *
 * Abstract contract that allows children to implement an
 * emergency stop mechanism. Differs from Pausable by causing a throw when in halt mode.
 *
 *
 * Originally envisioned in FirstBlood ICO contract.
 */
contract Haltable is Ownable {
    bool public halted;

    modifier stopInEmergency {
        require(!halted);
        _;
    }

    modifier onlyInEmergency {
        require(halted);
        _;
    }

    // called by the owner on emergency, triggers stopped state
    function halt() external onlyOwner {
        halted = true;
    }

    // called by the owner on end of emergency, returns to normal state
    function unhalt() external onlyOwner onlyInEmergency {
        halted = false;
    }

}


/**
 * @title ERC20Basic
 * @dev Simpler version of ERC20 interface
 * @dev see https://github.com/ethereum/EIPs/issues/179
 */
contract ERC20Basic {
    uint256 public totalSupply;

    function balanceOf(address who) constant returns (uint256);

    function transfer(address to, uint256 value) returns (bool);

    event Transfer(address indexed from, address indexed to, uint256 value);
}


/**
 * @title ERC20 interface
 * @dev see https://github.com/ethereum/EIPs/issues/20
 */
contract ERC20 is ERC20Basic {
    function allowance(address owner, address spender) constant returns (uint256);

    function transferFrom(address from, address to, uint256 value) returns (bool);

    function approve(address spender, uint256 value) returns (bool);

    event Approval(address indexed owner, address indexed spender, uint256 value);
}


/**
 * @title Basic token
 * @dev Basic version of StandardToken, with no allowances.
 */
contract BasicToken is ERC20Basic {
    using SafeMath for uint256;

    mapping(address => uint256) balances;

    /**
    * @dev transfer token for a specified address
    * @param _to The address to transfer to.
    * @param _value The amount to be transferred.
    */
    function transfer(address _to, uint256 _value) returns (bool) {
        balances[msg.sender] = balances[msg.sender].sub(_value);
        balances[_to] = balances[_to].add(_value);
        Transfer(msg.sender, _to, _value);
        return true;
    }

    /**
    * @dev Gets the balance of the specified address.
    * @param _owner The address to query the the balance of.
    * @return An uint256 representing the amount owned by the passed address.
    */
    function balanceOf(address _owner) constant returns (uint256 balance) {
        return balances[_owner];
    }

}


/**
 * @title Standard ERC20 token
 *
 * @dev Implementation of the basic standard token.
 * @dev https://github.com/ethereum/EIPs/issues/20
 * @dev Based on code by FirstBlood: https://github.com/Firstbloodio/token/blob/master/smart_contract/FirstBloodToken.sol
 */
contract StandardToken is ERC20, BasicToken {

    mapping(address => mapping(address => uint256)) allowed;


    /**
     * @dev Transfer tokens from one address to another
     * @param _from address The address which you want to send tokens from
     * @param _to address The address which you want to transfer to
     * @param _value uint256 the amout of tokens to be transfered
     */
    function transferFrom(address _from, address _to, uint256 _value) returns (bool) {
        var _allowance = allowed[_from][msg.sender];

        // Check is not needed because sub(_allowance, _value) will already throw if this condition is not met
        // require (_value <= _allowance);

        balances[_to] = balances[_to].add(_value);
        balances[_from] = balances[_from].sub(_value);
        allowed[_from][msg.sender] = _allowance.sub(_value);
        Transfer(_from, _to, _value);
        return true;
    }

    /**
     * @dev Aprove the passed address to spend the specified amount of tokens on behalf of msg.sender.
     * @param _spender The address which will spend the funds.
     * @param _value The amount of tokens to be spent.
     */
    function approve(address _spender, uint256 _value) returns (bool) {

        // To change the approve amount you first have to reduce the addresses`
        //  allowance to zero by calling `approve(_spender, 0)` if it is not
        //  already 0 to mitigate the race condition described here:
        //  https://github.com/ethereum/EIPs/issues/20#issuecomment-263524729
        require((_value == 0) || (allowed[msg.sender][_spender] == 0));

        allowed[msg.sender][_spender] = _value;
        Approval(msg.sender, _spender, _value);
        return true;
    }

    /**
     * @dev Function to check the amount of tokens that an owner allowed to a spender.
     * @param _owner address The address which owns the funds.
     * @param _spender address The address which will spend the funds.
     * @return A uint256 specifing the amount of tokens still avaible for the spender.
     */
    function allowance(address _owner, address _spender) constant returns (uint256 remaining) {
        return allowed[_owner][_spender];
    }

}


/**
 * @title VeraCoin
 * @dev Very simple ERC20 Token example, where all tokens are pre-assigned to the creator.
 * Note they can later distribute these tokens as they wish using `transfer` and other
 * `StandardToken` functions.
 */
contract VeraCoin is StandardToken {

    string public name = "VeraCoin";

    string public symbol = "Vera";

    uint256 public decimals = 18;

    uint256 public INITIAL_SUPPLY = 15700000 * 1 ether;

    /**
    * @dev Contructor that gives msg.sender all of existing tokens.
    */
    function VeraCoin() {
        totalSupply = INITIAL_SUPPLY;
        balances[msg.sender] = INITIAL_SUPPLY;
    }
}


contract VeraCoinPreSale is Haltable {
    using SafeMath for uint;

    string public name = "VeraCoin PreSale";

    VeraCoin public token;

    address public beneficiary;

    uint256 public hardCap;

    uint256 public softCap;

    uint256 public collected;

    uint256 public price;

    uint256 public tokensSold = 0;

    uint256 public weiRaised = 0;

    uint256 public investorCount = 0;

    uint256 public weiRefunded = 0;

    uint256 public startTime;

    uint256 public endTime;

    bool public softCapReached = false;

    bool public crowdsaleFinished = false;

    mapping(address => bool) refunded;

    event GoalReached(uint256 amountRaised);

    event SoftCapReached(uint256 softCap);

    event NewContribution(address indexed holder, uint256 tokenAmount, uint256 etherAmount);

    event Refunded(address indexed holder, uint256 amount);

    modifier onlyAfter(uint256 time) {
        require(now >= time);
        _;
    }

    modifier onlyBefore(uint256 time) {
        require(now <= time);
        _;
    }

    function VeraCoinPreSale(
        uint256 _hardCapUSD,
        uint256 _softCapUSD,
        address _token,
        address _beneficiary,
        uint256 _totalTokens,
        uint256 _priceETH,

        uint256 _startTime,
        uint256 _duration
    ) {
        hardCap = _hardCapUSD * 1 ether / _priceETH;
        softCap = _softCapUSD * 1 ether / _priceETH;
        price = _totalTokens * 1 ether / hardCap;

        token = VeraCoin(_token);
        beneficiary = _beneficiary;

        startTime = _startTime;
        endTime = _startTime + _duration * 1 hours;
    }

    function() payable stopInEmergency {
        require(msg.value >= 0.01 * 1 ether);
        doPurchase(msg.sender);
    }

    function refund() external onlyAfter(endTime) {
        require(!softCapReached);
        require(!refunded[msg.sender]);

        uint256 balance = token.balanceOf(msg.sender);
        require(balance > 0);

        uint256 refund = balance / price;
        if (refund > this.balance) {
            refund = this.balance;
        }

        require(msg.sender.send(refund));
        refunded[msg.sender] = true;
        weiRefunded = weiRefunded.add(refund);
        Refunded(msg.sender, refund);
    }

    function withdraw() onlyOwner {
        require(softCapReached);
        require(beneficiary.send(collected));
        token.transfer(beneficiary, token.balanceOf(this));
        crowdsaleFinished = true;
    }

    function doPurchase(address _owner) private onlyAfter(startTime) onlyBefore(endTime) {
        require(!crowdsaleFinished);
        require(collected.add(msg.value) <= hardCap);

        if (!softCapReached && collected < softCap && collected.add(msg.value) >= softCap) {
            softCapReached = true;
            SoftCapReached(softCap);
        }

        uint256 tokens = msg.value * price;

        if (token.balanceOf(msg.sender) == 0) investorCount++;

        collected = collected.add(msg.value);

        token.transfer(msg.sender, tokens);

        weiRaised = weiRaised.add(msg.value);
        tokensSold = tokensSold.add(tokens);

        NewContribution(_owner, tokens, msg.value);

        if (collected == hardCap) {
            GoalReached(hardCap);
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
        emit CVRevoked(_vac, _cv, msg.sender);
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
