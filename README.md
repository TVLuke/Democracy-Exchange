# Democracy Exchange

[![Tests](https://github.com/TVLuke/Democracy-Exchange/actions/workflows/tests.yml/badge.svg)](https://github.com/TVLuke/Democracy-Exchange/actions/workflows/tests.yml)
[![Codeberg Sync](https://github.com/TVLuke/Democracy-Exchange/actions/workflows/codeberg-mirror.yml/badge.svg)](https://github.com/TVLuke/Democracy-Exchange/actions/workflows/codeberg-mirror.yml)


**Note: This very much is just a quick thing i threw together in an afternoon or two out of curiosity. It may be useful to someone. But this is not great code and it is not completly tested. Use at your own risk.**

There are many parliamentary democracies. For people living in them, their elections probably feel normal. But every country does it differently. People vote everywhere, but what they vote for, how they do it, and what gets counted varies. The way votes turn into seats and majorities is different too.

**This is a stupid idea to learn about the diferent ways we count votes by projecting the votes from one country with the electoral-system in another country.**

These examples use mostly elections for the lower houeses, like the House of Commons in the United Kingdom, the German Bundestag, the Austrian Nationalrat, the French National Assembly and the US House of Representatives.

Of course the electoral system shapes the party-landscape. Strategies and systems for a tactical vote emerge from the rules. So these projections are not actually legitimate, since people would vote differently if the system was different. But they: 

- a) may help understand how different ways of counting votes shape the way a paralement can look and
- b) how different countries systems have advantages and disatvantages.

## How to use

1. Clone the repo:
```bash
git clone https://github.com/TVLuke/Democracy-Exchange.git
cd Democracy-Exchange
```

2. Create and activate a virtual environment:
```bash
# On macOS/Linux
python -m venv venv
source venv/bin/activate

# On Windows
python -m venv venv
venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Run the script:
```bash
python main.py
```

To change which votes to pair with which electoral system, edit the `country`, `year` and `appointments` variables in `main.py`:

```
# Set up election parameters
country = 'germany'
year = '2021'
election = country + year

appointments = ['austria']
```

You can run multiple appointments.

Examples:

![Example 1: Showing a seat distribution in a parlament](docs/example1.png)

![Example 2: Showing Bar Charts.](docs/example2.png)

![Example 3: Showing possible coalitions between parties](docs/example3.png)

![Example 4: More bar charts](docs/example4.png)

The `main.py` also genrates reports, which can be found in the `reports` folder.

Example:

[The german election using the uk election system](reports/germany2021_uk_report.md)

## How to add new Elections and Appointments

### Elections

There is a subfolder for each election named by the country and year, like `germany2021`.

We start with raw data. There are several things that are true for most democracies today. They have parties and they have divided the country into some sort of electoral districts, in which voting takes place.

We try to collect demographic data on the size of the electorate (people eligible to vote), number of citizens (people who are citizens), and population for each district and state. These may be relevant in some election systems for the distribution of seats (Austria does a distribution of parliament seats per state by number of citizens but calculates vote-share by a factor including the size of the electorate, the US uses distribution by state population). If one is not available, we use another as fallback.

This is all done using open data from the web. Usually there should be a README.md inside the folder to point to the sources and provide information about the licenses.

From the raw data we create several files: 

- `participating_parties.json` contains a list of parties with some helpful information for the graphical representation, like the color they are usually represented in. This also has a value left_to_right which is used to determine the seating order of parties in parliament (and thus, how they should be displayed in a seating graph). Parties can have the flag minority=true for electoral systems that have special rules for parties representing minorities.

An extract of the file may look like this:

```
  {
    "short_name": "SPD",
    "name": "",
    "color": "#eb001f",
    "left_to_right": 4
  },
  {
    "short_name": "SSW",
    "name": "",
    "color": "#EFEFEF",
    "left_to_right": 3,
    "minority": true
  },
```

- `voting_district_results.json` contains the results of the electoral districts, with the number of votes for each party in each district. These are categorized either as list votes or member votes, depending if the type of voting is by party-list or voting directly for a member of parliament. Some countries (for example Germany) have both. Also, it contains number of electorate, citizens and population for district if known.

An extract may look like this:

```
{
    "district": 141,
    "name": "Herne – Bochum II",
    "state": "Nordrhein-Westfalen",
    "population": 243909,
    "electorate": 173939,
    "party_results": {
      "CDU": {
        "member": 24027,
        "list": 23164
      },
      "SPD": {
        "member": 52792,
        "list": 46578
      },
      "FDP": {
        "member": 8455,
        "list": 10623
      },
      "AfD": {
        "member": 11863,
        "list": 11882
      },
      "GRÜNE": {
        "member": 14262,
        "list": 15383
      },
      "DIE LINKE": {
        "member": 4667,
        "list": 5029
      },
      "Die PARTEI": {
        "member": 2550,
        "list": 1467
      },
      "Tierschutzpartei": {
        "member": 0,
        "list": 2357
      },
      "PIRATEN": {
        "member": 0,
        "list": 582
      },
      "FREIE WÄHLER": {
        "member": 1423,
        "list": 818
      },
      "HEIMAT (2021: NPD)": {
        "member": 0,
        "list": 168
      },
      "ÖDP": {
        "member": 0,
        "list": 76
      },
      "V-Partei³": {
        "member": 0,
        "list": 110
      },
      "Verjüngungsforschung (2021: Gesundheitsforschung)": {
        "member": 0,
        "list": 169
      },
      "MLPD": {
        "member": 220,
        "list": 124
      },
      "Die Humanisten": {
        "member": 0,
        "list": 109
      },
      "DKP": {
        "member": 0,
        "list": 34
      },
      "SGP": {
        "member": 0,
        "list": 11
      },
      "dieBasis": {
        "member": 1251,
        "list": 927
      },
      "Bündnis C": {
        "member": 0,
        "list": 68
      },
      "du.": {
        "member": 0,
        "list": 67
      },
      "LIEBE": {
        "member": 0,
        "list": 226
      },
      "Wir Bürger (2021: LKR)": {
        "member": 0,
        "list": 46
      },
      "PdF": {
        "member": 0,
        "list": 49
      },
      "LfK": {
        "member": 0,
        "list": 106
      },
      "Team Todenhöfer": {
        "member": 0,
        "list": 1395
      },
      "Volt": {
        "member": 0,
        "list": 273
      }
    }
  },
```

- `basic_information.json` includes some basic information, like the name of the election, the year and the number of seats.

For example:

```
    {
    "name": "Stimmen der Wahl zum Deutschen Bundestag 2021",
    "date": 2021,
    "seats": 733
    }
```

- `states.json` contains a list of all states. It should contain data on electorate, citizens and population.

Like:

```
"Schleswig-Holstein": {
    "name": "Schleswig-Holstein",
    "population": 2668990,
    "electorate": 2272717
  },
  "Mecklenburg-Vorpommern": {
    "name": "Mecklenburg-Vorpommern",
    "population": 1494603,
    "electorate": 1314435
  },
```

Each election also needs a file `country_specific_voting_data_changes.py` with a function 

```
def changes_for_country(voting_data: list, parties: list) -> list:
```

Which modifies the raw data from `participating_parties.json` and `voting_district_results.json` before it is sent to an election system. This takes care of such oddities as CDU and CSU being two parties but usually being seen as one in Germany or the seat of the speaker in the UK not being counted as the party they belong to.

Then there are folders without a year, these are the electoral systems in `election.py`.

This always has a function 

```
def calculate_seats(results: list, states: list, total_seats: int, participating_parties: list) -> List[Party]:
```

This is the main function to be called from the `main.py`.

This calculates the seat distribution and returns it. There is also a `basic_information.json` which contains information about the election, especially if it is a list or member election.

### Graphics
Graphics are created by `plotparlament.py` and `vote_distribution.py` which are called from `main.py`.

The graphics for interpreting the German election as a US presidential election are completely separate from that and are all contained in `president.py`.

## Tests

The tests are fairly simple, we just use the data from an election on its own system. The result should be the actual seat distribution from that election. If that happens we probably got this somewhat right. Or not too wrong.

Tests are automatically run on GitHub's infrastructure using GitHub Actions whenever code is pushed to the main branch or when a pull request is created. This helps ensure that changes don't break existing functionality. You can see the test results in the "Actions" tab of the repository.

# Note on Use of LLMs

This code was created using, among other tools, LLM tools like ChatGPT.
