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

    mapping (address => uint256) balances;

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

    mapping (address => mapping (address => uint256)) allowed;


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

    mapping (address => bool) refunded;

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

contract Accessable {
    mapping (address => bool) public allowed_contracts;

    event GrantAccess(address sender, address allowed, uint256);

    event RevokeAccess(address sender, address allowed, uint256);

    function Accessable() {
        allowed_contracts[msg.sender] = true;
    }

    modifier onlyAllowed() {
        require(allowed_contracts[msg.sender]);
        _;
    }

    function grant_access(address _address) public onlyAllowed {
        allowed_contracts[_address] = true;
        GrantAccess(msg.sender, _address, now);
    }

    function revoke_access(address _address) public onlyAllowed {
        allowed_contracts[_address] = false;
        RevokeAccess(msg.sender, _address, now);
    }
}

contract VeraOracle is Ownable {

    using SafeMath for uint256;

    address public token;

    string public name;

    enum State {_, enabled, disabled}

    struct State_dict {
        mapping (address => State) dict;
        address[] keys;
    }

    State_dict employers;

    State_dict candidates;

    event NewEmployer(address indexed employer_address, uint256 time);

    event DisabledEmployer(address employer_address, uint256 time);

    event EnabledEmployer(address employer_address, uint256 time);

    event NewCandidate(address indexed candidate_address, uint256 time);

    event DisabledCandidate(address candidate_address, uint256 time);

    event EnabledCandidate(address candidate_address, uint256 time);

    modifier onlyEnabledEmployer(address _address) {
        require(employers.dict[_address] == State.enabled);
        _;
    }

    modifier onlyDisabledEmployer(address _address) {
        require(employers.dict[_address] == State.disabled);
        _;
    }

    modifier onlyEnabledCandidate(address _address) {
        require(candidates.dict[_address] == State.enabled);
        _;
    }

    modifier onlyDisabledCandidate(address _address) {
        require(candidates.dict[_address] == State.disabled);
        _;
    }

    function VeraOracle(address _token, string _name) public {
        token = _token;
        name = _name;
    }

    function get_employers() public view returns(address[]) {
        return employers.keys;
    }

    function get_candidates() public view returns(address[]){
        return candidates.keys;
    }

    function new_employer(bytes32 _id, address _token) public onlyOwner returns(bool) {
        Employer employer = new Employer(_id, _token);
        employers.dict[employer] = State.enabled;
        employers.keys.push(employer);
        grant_access(employer, msg.sender);
        NewEmployer(employer, now);
        return true;
    }

    function get_employer_id(address _address) public view returns(bytes32) {
        return Employer(_address).id();
    }

    function disable_employer(address _address) public onlyOwner onlyEnabledEmployer(_address) {
        employers.dict[_address] = State.disabled;
        DisabledEmployer(_address, now);
    }

    function enable_employer(address _address) public onlyOwner onlyDisabledEmployer(_address) {
        employers.dict[_address] = State.enabled;
        EnabledEmployer(_address, now);
    }

    function get_employer_state(address _address) public view returns(State) {
        return employers.dict[_address];
    }

    function new_candidate(bytes32 _id) public onlyOwner returns(bool) {
        Candidate candidate = new Candidate(_id);
        candidates.dict[candidate] = State.enabled;
        candidates.keys.push(candidate);
        grant_access(candidate, msg.sender);
        NewCandidate(candidate, now);
        return true;
    }

    function get_candidate_id(address _address) public view returns(bytes32) {
        return Candidate(_address).id();
    }

    function disable_candidate(address _address) public onlyOwner onlyEnabledCandidate(_address) {
        candidates.dict[_address] = State.disabled;
        DisabledCandidate(_address, now);
    }

    function enable_candidate(address _address) public onlyOwner onlyDisabledCandidate(_address) {
        candidates.dict[_address] = State.enabled;
        EnabledCandidate(_address, now);
    }

    function get_candidate_state(address _address) public view returns(State) {
        return candidates.dict[_address];
    }

    function new_vacancy(address _employer_contract, uint256 _allowed_amount, uint256 _interview_fee) public onlyOwner onlyEnabledEmployer(_employer_contract) returns(bool) {
        Employer(_employer_contract).new_vacancy(_allowed_amount, _interview_fee);
        return true;
    }

    function disable_vacancy(address _employer_contract, address _vacancy_contract) public onlyOwner onlyEnabledEmployer(_employer_contract) {
        Employer(_employer_contract).disable_vacancy(_vacancy_contract);
    }

    function enable_vacancy(address _employer_contract, address _vacancy_contract) public onlyOwner onlyEnabledEmployer(_employer_contract) {
        Employer(_employer_contract).enable_vacancy(_vacancy_contract);
    }

    function grant_access(address _contract, address _allowed_contract) public onlyOwner {
        Accessable(_contract).grant_access(_allowed_contract);
    }

    function revoke_access(address _contract, address _allowed_contract) public onlyOwner {
        Accessable(_contract).revoke_access(_allowed_contract);
    }

    function pay_to_candidate(address _employer_address, address _vacancy_address, address _candidate_address) onlyOwner {
        Employer(_employer_address).pay_to_candidate(_vacancy_address, _candidate_address);
    }
}

contract Employer is Accessable {

    using SafeMath for uint256;

    enum State {_, enabled, disabled}

    struct State_dict {
        mapping (address => State) dict;
        address[] keys;
    }

    bytes32 public id;

    address public token;

    State_dict vacancies;

    event NewVacancy(address indexed vacancy_address, uint256 time);

    event DisabledVacancy(address indexed vacancy_address, uint256 time);

    event EnabledVacancy(address indexed vacancy_address, uint256 time);

    modifier onlyEnabledVacancy(address _address) {
        require(vacancies.dict[_address] == State.enabled);
        _;
    }

    modifier onlyDisabledVacancy(address _address) {
        require(vacancies.dict[_address] == State.disabled);
        _;
    }

    function Employer(bytes32 _id, address _token) public {
        id = _id;
        token = _token;
    }

    function new_vacancy(uint256 _allowed_amount, uint256 _interview_fee) public onlyAllowed {
        Vacancy vacancy = new Vacancy(_interview_fee);
        require(ERC20(token).approve(vacancy, _allowed_amount));
        vacancies.dict[vacancy] = State.enabled;
        vacancies.keys.push(vacancy);
        NewVacancy(vacancy, now);
    }

    function disable_vacancy(address _address) public onlyAllowed onlyEnabledVacancy(_address) {
        vacancies.dict[_address] = State.disabled;
        DisabledVacancy(_address, now);
    }

    function enable_vacancy(address _address) public onlyAllowed onlyDisabledVacancy(_address) {
        vacancies.dict[_address] = State.enabled;
        EnabledVacancy(_address, now);
    }

    function get_vacancies() public view returns (address[]) {
        return vacancies.keys;
    }

    function get_vacancy_state(address _vacancy_address) public view returns(State) {
        return vacancies.dict[_vacancy_address];
    }

    function grant_access_to_candidate(address _vacancy_address, address _candidate_address) public onlyAllowed onlyEnabledVacancy(_vacancy_address) {
        Vacancy(_vacancy_address).grant_candidate(_candidate_address);
    }

    function revoke_access_to_candidate(address _vacancy_address, address _candidate_address) public onlyAllowed onlyEnabledVacancy(_vacancy_address) {
        Vacancy(_vacancy_address).revoke_candidate(_candidate_address);
    }

    function pay_to_candidate(address _vacancy_address, address _candidate_address) public onlyAllowed onlyEnabledVacancy(_vacancy_address) {
        Vacancy(_vacancy_address).pay_to_candidate(_candidate_address, token);
    }
}

contract Vacancy is Ownable {

    using SafeMath for uint256;

    uint256 public interview_fee;

    enum Interview_phase {_, wait, accepted, paid, revoked}

    struct Interview_phase_dict {
        mapping (address => Interview_phase) dict;
        address[] keys;
    }

    mapping (address => bool) public is_paid;

    Interview_phase_dict candidates_to_interview;

    event CandidateGrantAccess(address indexed candidate);

    event CandidateRevokeAccess(address indexed candidate);

    modifier onlyNotExist() {
        require(candidates_to_interview.dict[msg.sender] == Interview_phase._);
        _;
    }

    modifier onlyExist() {
        require(candidates_to_interview.dict[msg.sender] != Interview_phase._);
        _;
    }

    modifier onlyAccepted(address _address) {
        require(candidates_to_interview.dict[_address] == Interview_phase.accepted);
        _;
    }

    function Vacancy(uint256 _interview_fee) public {
        interview_fee = _interview_fee;
    }

    function get_candidates() public view returns(address[]) {
        return candidates_to_interview.keys;
    }

    function get_candidate_state(address _candidate_address) public view returns (Interview_phase) {
        return candidates_to_interview.dict[_candidate_address];
    }

    function subscribe_to_interview() public onlyNotExist returns(bool) {
        candidates_to_interview.dict[msg.sender] = Interview_phase.wait;
        candidates_to_interview.keys.push(msg.sender);
        return true;
    }

    function unsubscribe_from_interview() public onlyExist returns(bool) {
        candidates_to_interview.dict[msg.sender] = Interview_phase._;
        return true;
    }

    function grant_candidate(address _candidate_address) public onlyOwner returns(bool) {
        candidates_to_interview.dict[_candidate_address] = Interview_phase.accepted;
        Candidate(_candidate_address).employer_accept(this);
        CandidateGrantAccess(_candidate_address);
        return true;
    }

    function revoke_candidate(address _candidate_address) public onlyOwner returns(bool) {
        candidates_to_interview.dict[_candidate_address] = Interview_phase.revoked;
        Candidate(_candidate_address).employer_revoke(this);
        CandidateRevokeAccess(_candidate_address);
        return true;
    }

    function pay_to_candidate(address _candidate_address, address _token) public onlyOwner onlyAccepted(_candidate_address) returns(bool) {
        require(!is_paid[_candidate_address]);
        require(Candidate(_candidate_address).set_vacancy_paid(this));
        candidates_to_interview.dict[_candidate_address] = Interview_phase.paid;
        ERC20(_token).transferFrom(msg.sender, _candidate_address, interview_fee);
        is_paid[_candidate_address] = true;
        return true;
    }
}

contract Candidate is Accessable, Ownable {

    bytes32 public id;

    enum Phase {_, wait, accepted, paid, revoked}

    struct Fact {
        address from;
        uint256 time;
        string fact;
    }

    struct Fact_dict {
        mapping(bytes32 => Fact) dict;
        bytes32[] keys;
    }

    struct Vacancies_dict {
        mapping (address => Phase) dict;
        address[] keys;
    }

    Fact_dict facts;

    Vacancies_dict vacancies;

    event NewFact(address sender, uint256 time, bytes32 id);

    modifier vacancyPhase(address _address, Phase _phase) {
        require(vacancies.dict[_address] == _phase);
        _;
    }

    function Candidate(bytes32 _id) public {
        id = _id;
    }

    function new_fact(string _fact) public onlyAllowed returns(bool) {
        bytes32 _id = sha3(_fact);
        facts.dict[_id] = Fact(msg.sender, now, _fact);
        facts.keys.push(_id);
        NewFact(msg.sender, now, _id);
        return true;
    }

    function keys_of_facts() public view returns(bytes32[]) {
        return facts.keys;
    }

    function get_fact(bytes32 _id) public view returns(address from, uint256 time, string fact) {
        return (facts.dict[_id].from, facts.dict[_id].time, facts.dict[_id].fact);
    }

    function subscribe_to_interview(address _vacancy_address) public onlyAllowed {
        require(vacancies.dict[_vacancy_address] == Phase._);
        require(Vacancy(_vacancy_address).subscribe_to_interview());
        vacancies.dict[_vacancy_address] = Phase.wait;
        vacancies.keys.push(_vacancy_address);
    }

    function get_vacancies() public view returns(address[]) {
        return vacancies.keys;
    }

    function get_vacancy_state(address _vacancy) public view returns(Phase) {
        return vacancies.dict[_vacancy];
    }

    function unsubscribe_from_interview(address _vacancy_address) public onlyAllowed {
        require(vacancies.dict[_vacancy_address] == Phase.wait);
        require(Vacancy(_vacancy_address).unsubscribe_from_interview());
        vacancies.dict[_vacancy_address] = Phase._;
    }

    function employer_accept(address _vacancy_address)  vacancyPhase(_vacancy_address, Phase.wait) returns(bool) {
        vacancies.dict[_vacancy_address] = Phase.accepted;
    }

    function employer_revoke(address _vacancy_address) public vacancyPhase(_vacancy_address, Phase.wait) returns(bool) {
        vacancies.dict[_vacancy_address] = Phase.revoked;
        return true;
    }

    function set_vacancy_paid(address _vacancy_address) public vacancyPhase(_vacancy_address, Phase.accepted) returns(bool) {
        vacancies.dict[_vacancy_address] = Phase.paid;
        return true;
    }
}