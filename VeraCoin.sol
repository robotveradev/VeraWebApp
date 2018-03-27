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

contract PermissionedAgents {
    mapping(address => bool) public agents;

    event GrantAgent(address sender, address allowed, uint256);

    event RevokeAgent(address sender, address allowed, uint256);

    function PermissionedAgents() {
        agents[msg.sender] = true;
    }

    modifier onlyAgent() {
        require(agents[msg.sender]);
        _;
    }

    function grant_access(address _address) public onlyAgent {
        agents[_address] = true;
        GrantAgent(msg.sender, _address, now);
    }

    function revoke_access(address _address) public onlyAgent {
        agents[_address] = false;
        RevokeAgent(msg.sender, _address, now);
    }
}

contract Pausable is PermissionedAgents {
    event Pause();
    event Unpause();

    bool public paused = false;

    modifier whenNotPaused() {
        require(!paused);
        _;
    }

    modifier whenPaused() {
        require(paused);
        _;
    }

    function pause() onlyAgent whenNotPaused public {
        paused = true;
        Pause();
    }

    function unpause() onlyAgent whenPaused public {
        paused = false;
        Unpause();
    }
}


contract Withdrawable is Pausable {
    function withdraw(address _token, address _to, uint256 _amount) public onlyAgent {
        ERC20Basic(_token).transfer(_to, _amount);
    }
}

contract VeraOracle is Ownable {

    using SafeMath for uint256;

    bytes32 public name;

    address[] public employers;

    address[] public candidates;

    uint8 public service_fee;

    uint256 public vacancy_fee;

    address public beneficiary;

    address public token;

    event NewEmployer(address employer_address);

    event NewCandidate(address candidate_address);

    //"vera",5,"0xca35b7d915458ef540ade6068dfe2f44e8fa733c",25,"0x692a70d2e424a56d2c6c27aa97d1a86395877b3a"
    function VeraOracle(bytes32 _name, uint8 _service_fee, address _beneficiary, uint256 _vacancy_fee, address _token) public {
        name = _name;
        service_fee = _service_fee;
        beneficiary = _beneficiary;
        vacancy_fee = _vacancy_fee;
        token = _token;
    }

    function new_service_fee(uint8 _service_fee) public onlyOwner {
        service_fee = _service_fee;
    }

    function new_beneficiary(address _beneficiary) public onlyOwner {
        beneficiary = _beneficiary;
    }

    function new_vacancy_fee(uint256 _vacancy_fee) public onlyOwner {
        vacancy_fee = _vacancy_fee;
    }

    function new_employer(bytes32 _id) public onlyOwner {
        Employer employer = new Employer(_id, token);
        employers.push(employer);
        employer.grant_access(msg.sender);
        NewEmployer(employer);
    }

    function get_employers() public view returns (address[]) {
        return employers;
    }

    function new_candidate(bytes32 _id) public onlyOwner {
        Candidate candidate = new Candidate(_id);
        candidates.push(candidate);
        candidate.grant_access(msg.sender);
        NewCandidate(candidate);
    }

    function get_candidates() public view returns (address[]) {
        return candidates;
    }

    function new_vacancy(address _employer, uint256 _allowed_amount, uint256 _interview_fee) public {
        EmployerInterface(_employer).new_vacancy(_allowed_amount, _interview_fee, beneficiary, vacancy_fee);
    }

    function pay_to_candidate(address _employer_address, address _candidate_address, address _vacancy_address) onlyOwner public {
        EmployerInterface(_employer_address).pay_to_candidate(_vacancy_address, _candidate_address, beneficiary, service_fee);
    }

    function withdraw(address _token, address _from, address _to, uint256 _amount) public onlyOwner {
        Withdrawable(_from).withdraw(_token, _to, _amount);
    }
}

interface EmployerInterface {
    function new_vacancy(uint256 _allowed_amount, uint256 _interview_fee, address _beneficiary, uint256 _vacancy_fee) public;
    function get_vacancies() public view returns (address[]);
    function pause_vacancy(address _vacancy_address) public;
    function unpause_vacancy(address _vacancy_address) public;
    function grant_access_to_candidate(address _vacancy_address, address _candidate_address) public;
    function revoke_access_to_candidate(address _vacancy_address, address _candidate_address) public;
    function pay_to_candidate(address _vacancy_address, address _candidate_address, address _beneficiary, uint8 _service_fee) public;
}

contract Employer is EmployerInterface, Withdrawable {

    using SafeMath for uint256;

    bytes32 public id;

    address public token;

    address[] public vacancies;

    event NewVacancy(address vacancy_address);

    function Employer(bytes32 _id, address _token) public {
        id = _id;
        token = _token;
    }

    function new_vacancy(uint256 _allowed_amount, uint256 _interview_fee, address _beneficiary, uint256 _vacancy_fee) public onlyAgent whenNotPaused {
        Vacancy vacancy = new Vacancy(_interview_fee);
        require(ERC20Basic(token).transfer(_beneficiary, _vacancy_fee));
        require(ERC20(token).approve(vacancy, _allowed_amount));
        vacancies.push(vacancy);
        NewVacancy(vacancy);
    }

    function new_vacancy(address _vacancy_address) public onlyAgent whenNotPaused {
        vacancies.push(_vacancy_address);
        NewVacancy(_vacancy_address);
    }

    function get_vacancies() public view returns (address[]) {
        return vacancies;
    }

    function pause_vacancy(address _vacancy_address) public onlyAgent {
        Pausable(_vacancy_address).pause();
    }

    function unpause_vacancy(address _vacancy_address) public onlyAgent {
        Pausable(_vacancy_address).unpause();
    }

    function grant_access_to_candidate(address _vacancy_address, address _candidate_address) public onlyAgent {
        VacancyInterface(_vacancy_address).grant_candidate(_candidate_address);
    }

    function revoke_access_to_candidate(address _vacancy_address, address _candidate_address) public onlyAgent {
        VacancyInterface(_vacancy_address).revoke_candidate(_candidate_address);
    }

    function candidate_exam_fail(address _vacancy_address, address _candidate_address) public onlyAgent {
        VacancyInterface(_vacancy_address).candidate_failed(_candidate_address);
    }

    function pay_to_candidate(address _vacancy_address, address _candidate_address, address _beneficiary, uint8 _service_fee) public onlyAgent whenNotPaused {
        VacancyInterface(_vacancy_address).pay_to_candidate(_candidate_address, token, _beneficiary, _service_fee);
    }
}

interface VacancyInterface {
    function get_candidates() public view returns (address[]);
    function get_candidate_state(address _candidate_address) public view returns (Vacancy.Interview_phase);
    function subscribe_to_interview() public returns (bool);
    function grant_candidate(address _candidate_address) public;
    function revoke_candidate(address _candidate_address) public;
    function candidate_failed(address _candidate_address) public;
    function pay_to_candidate(address _candidate_address, address _token, address _beneficiary, uint8 _service_fee) returns (bool);
}

contract Vacancy is VacancyInterface, Ownable, Pausable {

    using SafeMath for uint256;

    uint256 public interview_fee;

    enum Interview_phase {_, wait, accepted, paid, revoked, failed}

    struct Interview_phase_dict {
        mapping(address => Interview_phase) dict;
        address[] keys;
    }

    Interview_phase_dict candidates_to_interview;

    event CandidateGrantAccess(address candidate);

    event CandidateRevokeAccess(address candidate);

    event CandidateFailExam(address candidate);

    modifier onlyNotExist() {
        require(candidates_to_interview.dict[msg.sender] == Interview_phase._);
        _;
    }

    modifier onlyAccepted(address _address) {
        require(candidates_to_interview.dict[_address] == Interview_phase.accepted);
        _;
    }

    modifier onlyNotPaid(address _address) {
        require(candidates_to_interview.dict[_address] != Interview_phase.paid);
        _;
    }

    function Vacancy(uint256 _interview_fee) public {
        interview_fee = _interview_fee;
    }

    function get_candidates() public view returns (address[]) {
        return candidates_to_interview.keys;
    }

    function get_candidate_state(address _candidate_address) public view returns (Interview_phase) {
        return candidates_to_interview.dict[_candidate_address];
    }

    function subscribe_to_interview() public onlyNotExist whenNotPaused returns (bool) {
        candidates_to_interview.dict[msg.sender] = Interview_phase.wait;
        candidates_to_interview.keys.push(msg.sender);
        return true;
    }

    function grant_candidate(address _candidate_address) public onlyOwner whenNotPaused {
        candidates_to_interview.dict[_candidate_address] = Interview_phase.accepted;
        CandidateGrantAccess(_candidate_address);
    }

    function revoke_candidate(address _candidate_address) public onlyOwner {
        candidates_to_interview.dict[_candidate_address] = Interview_phase.revoked;
        CandidateRevokeAccess(_candidate_address);
    }

    function candidate_failed(address _candidate_address) public onlyOwner {
        candidates_to_interview.dict[_candidate_address] = Interview_phase.failed;
        CandidateFailExam(_candidate_address);
    }

    function pay_to_candidate(address _candidate_address, address _token, address _beneficiary, uint8 _service_fee) public onlyOwner onlyAccepted(_candidate_address) onlyNotPaid(_candidate_address) whenNotPaused returns (bool) {
        uint256 candidate_fee = interview_fee - (interview_fee / 100 * _service_fee);
        uint256 service_fee = interview_fee - candidate_fee;
        ERC20(_token).transferFrom(msg.sender, _beneficiary, service_fee);
        ERC20(_token).transferFrom(msg.sender, _candidate_address, candidate_fee);
        candidates_to_interview.dict[_candidate_address] = Interview_phase.paid;
        return true;
    }
}

contract Candidate is Withdrawable {

    bytes32 public id;

    struct Fact {
        address from;
        uint256 time;
        string fact;
    }

    struct Fact_dict {
        mapping(bytes32 => Fact) dict;
        bytes32[] keys;
    }

    Fact_dict facts;

    address[] public vacancies;

    event NewFact(address sender, bytes32 id);

    function Candidate(bytes32 _id) public {
        id = _id;
    }

    function new_fact(string _fact) public onlyAgent {
        bytes32 _id = keccak256(_fact);
        facts.dict[_id] = Fact(msg.sender, now, _fact);
        facts.keys.push(_id);
        NewFact(msg.sender, _id);
    }

    function keys_of_facts() public view returns (bytes32[]) {
        return facts.keys;
    }

    function get_fact(bytes32 _id) public view returns (address from, uint256 time, string fact) {
        return (facts.dict[_id].from, facts.dict[_id].time, facts.dict[_id].fact);
    }

    function subscribe_to_interview(address _vacancy_address) public whenNotPaused onlyAgent {
        require(VacancyInterface(_vacancy_address).subscribe_to_interview());
        vacancies.push(_vacancy_address);
    }

    function get_vacancies() public view returns (address[]){
        return vacancies;
    }
}
