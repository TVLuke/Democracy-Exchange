# Democratic System Exchange

There are lots of parlamentary democracies out there. An most likely, for people in them the wy their elections work seems 'normal'. However while in all elections people vote, what they vote exactly, how they do it, wht is actualy counted and how this transforms into parlamemntary seats and mojorities is different in every country.

This is a stupid idea to learn about the diferent ways we count votes by projecting the votes from one country with the electoral-system in another country.

Of course the electoral system shapes the landscape of parties and the way people vote tactically. so these projections are not actually legitimate. But they 

- a) may help understand how different ways of counting votes shape the way a paralement can look and
- b) how different countries systems have advantages and disatvantages.

## How we start

We start with raw data. There are several things that are true for most democracies today. The have parties and they have devided the country into some sort of electoral districts, in which voting takes place.

So, from the raw data we create two files: 

- `participating_parties.json` contains a list of parties with some helpfull information for the graphical representation, like the color they are usually represented in.
- `voting_district_results.json` contains the results of the electoral districts, with the number of votes for each party in each district. These are categorized either as list voptes or member votes, depending if the type of voting is by party-list or voting directly for a member of paralament. Some countries (for example Germany) have both.
 
For each election there is also a file basic_information.json which mostly contains the information how large the parlament is (how many members).