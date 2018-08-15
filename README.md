[![OnGrid Systems Blockchain Applications DApps Development](img/ongrid-systems-cover.png)](https://ongrid.pro/)

![GitHub last commit](https://img.shields.io/github/last-commit/robotveradev/VeraWebApp.svg)
![GitHub release](https://img.shields.io/github/release/robotveradev/VeraWebApp.svg)
[![Project website](https://img.shields.io/website-up-down-green-red/http/vera.jobs.svg?label=project-site)](https://vera.jobs)
[![Demo website](https://img.shields.io/website-up-down-green-red/http/demo.vera.jobs.svg?label=demo-site)](https://vera.wtf)
![License](https://img.shields.io/github/license/robotveradev/VeraWebApp.svg)

## VERA Web Application

### About

VERA is a platform for automating the recruitment process. The decentralized principles and built-in economical
motivation mechanism make it possible to transform hiring process, make it more transparent and seamless. 
VERA is the first job board service where candidates get paid for interviews and exams while looking for the job.
VERA is based on public [Ethereum](http://ethereum.org/) ledger containing open job positions and candidates' profiles around the world with 
comprehensive and trustworthy records of their experience, education and training. 
Native reward in [ERC-20](https://en.wikipedia.org/wiki/ERC-20) tokens provides strong motivation for prospective employees to apply for the position, 
take tests and pass interviews with the recruiter.

### Authorization

Essential information of vacancies and profiles is stored on blockchain so public by its nature. Any party can use 
Smart Contract registries as discovery point to search and retrieve public data.
To create and update their records, users have to be authorized. All the widely used traditional authorization and 
authentication mechanisms are supported including email and OAuth (Facebook, Google+,
Linkedin, etc.). Decentralized identity schemas and self-sovereign identities to be used in the future ([uPort](https://www.uport.me) is one of the
most promising protocols).

### Product features

* Applicant is able to register, fill and and publish his profile (CV). Profile information may include basic contact
information, work experience, professional skills and education, portfolio or cases. The indexed data is stored as 
on-chain claims in the Ethereum contract; 
* Multiple filters for vacancies and candidates profiles search: by Country, Region, Metro Station (if applicable), Salary,
Specialisation, Reward for interview/exam, Company name and so on;
* Phone verification via SMS or voice call
* Email verification
* Exam builder
* Interview configurator 
* Drop-out pipeline composer to build the series of tests/interviews with configurable reward per step.

### Hiring process

The process of hiring is a fixed sequence of steps — the candidate should traverse through pipeline built by employer.
The following steps are available by default:
* application for vacancy by the applicant / invitation of the applicant by the employer
* smart-filter — a sequence of questions from the employer that allows employer to assess the applicant by the measured parameter
* video interviews
* test exams
* face to face interviews

### Employment Pipeline

Employment pipeline is the sequence of filters, tests, interviews, approvals and other actions which constructed by the 
employer and complements the vacancy contract. Pipelines are built with feature-rich graphical constructor but enforced 
autonomously by Smart Contract. Pipeline and steps configuration, payout settings, minimal score threshold are specific 
for the vacancy. Candidates interested in the vacancy go through these steps and get evaluated, measured and either get 
allowance for the next step or get refused with detailed feedback. In addition, pipeline execution provides tokens reward f
or passing each step.

### Demo

You can try our product at [demo.vera.jobs](https://demo.vera.jobs).

## Ethereum smart contracts

VERA platform Ethereum smart contracts consist of
* **Oracle** - the central point for Platform logic;
* **Pipeline** contains actions to be passed by Candidate
* **Facts** registry storing 3rd parties claims
* **Company** contract of the hiring company

All contracts are located in separate [Github repository](https://github.com/robotveradev/SmartContracts)

## Built with

Currently due to its complex logic and lack of feature-rich serverless frameworks, the application is built on Django as 
traditional client-server application. As decentralized communication protocols and development tools evolve, become 
more lightweight, functional and stable, this service will be refactored to be serverless-as-possible.


* Blockchain: [Ethereum](https://www.ethereum.org) + [Solidity](https://github.com/ethereum/solidity) + [TruffleSuite](https://truffleframework.com)
* Frontend: [Material UI](https://material-ui.com) + [React](https://reactjs.org)
* Backend: [Django Web Framework](https://www.djangoproject.com) - to be reidesigned as serverless app
* Task Scheduler: [Celery](http://www.celeryproject.org) - won't be needed in serverless implementation 
* Message Queue: [RabbitMQ](http://rabbitmq.com/) - won't be needed after migration to serverless implementation

## Deployment

Instructions for Linux Ubuntu available at [Deployment guide](DEPLOYMENT.md).

## Team

* [Kirill Varlamov](https://github.com/ongrid)
* [Sergey Korotko](https://github.com/achievement008)
* [Dmitry Suldin](https://github.com/Klyaus)
* and other guys from [OnGrid Systems](https://github.com/OnGridSystems/)


## License

Copyright (c) 2018 ROBOTVERA OÜ,
> Narva mnt 36 Kesklinna linnaosa,
> Tallinn Harju maakond 10152

Each file included in this repository is licensed under the [MIT license](LICENSE).