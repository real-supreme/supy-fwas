# Supy-fwas [SFWAS]

[![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)](https://www.python.org/) [![GitHub](https://img.shields.io/badge/github-%23121011.svg?style=for-the-badge&logo=github&logoColor=white)](https://github.com/real-supreme/supy-fwas) [![Discord](https://img.shields.io/badge/Discord-%235865F2.svg?style=for-the-badge&logo=discord&logoColor=white)](https://discord.com/users/309963727913091073)

This is a wrapper library to easily retrieve FWA related information that is publicly available and free-to-use. The package uses synchronous calls for developers to easily implement the features.

# Table of Contents

1. [About the package](#supy-fwas-sfwas) 📦
2. [Usage](#usage) 🧾
	* [Installation](#installation) ➕
	* [Requirements](#requirements) ⚙
	* [Examples](#examples) 🖥
3. [License](#license) &copy;
4. [Disclaimer](#disclaimer) ❗
5. [Contact](#contact) 📩

## Usage

SFWAS focuses on easy-to-use Python synchronous methods and objects. See [Examples](#examples)

### Installation

For Windows:
```
py -m pip install supy-fwas
``` 

For Unix/MacOS:
```
python3 -m pip install supy-fwas
```

### Requirements

- Python 3.7+
	- coc.py 2.0+
	- requests

### Examples

This consists of only few out of all the available methods in the package.

-------------

```py
from sfwas import SFWAS

supy = SFWAS()

# Allows only FWA clan_tag to execute the function
# Other clan_tags are ignored
@supy.fwa_clans 
def foo1(clan_tag, member_tag):
	print(f"{member_tag} is now a part of clan ({clan_tag}))")
	# any suitable work 
	...

def foo2(clan_tag, ...):
	clan_weight = supy.get_clan_weight(clan_tag)
	...

def foo3(player_tag):
	w = supy.get_member_weight(player_tag)
	# If Exception `NotFound` is thrown, you'll require to use get_member_from_clan()
	# Since FWA Stats likely doesn't have their weights readily available

def bar(clan_name):
	clan_tag = supy.get_clan_by_name(clan_name)
	# Use clan_tag for any valid purpose :)
	
...
```

`foo1` Describes how the decorator helps the function filter/not call clans that are not in FWA Stats (FWA)

`foo2` Describes how easy it is to get the latest uploaded clan weights of a clan.

`foo3` Describes the use of *player_tag* to get player weights

`bar` Uses **get_member_weight()** method (instead of **get_member_weight_from_clan()**) to retrieve member's weight.

<p style="text-align: right;">
	<a href="#table-of-contents">Top</a>
</p>

## License

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE) 

Copyright (c) 2022-present real-supreme
<p style="text-align: right;">
	<a href="#table-of-contents">Top</a>
</p>

## Disclaimer

***This content is not affiliated with, endorsed, sponsored, or specifically approved by Supercell and Supercell is not responsible for it. For more information see Supercell's Fan Content Policy: www.supercell.com/fan-content-policy***

This package is not supported or developed by FWA. The package is used to access data directly from the [fwa stats](https://fwastats.com/).
<p style="text-align: right;">
	<a href="#table-of-contents">Top</a>
</p>

## Contact

- Discord - [SUPREME#1000](https://discord.com/channels/@me/309963727913091073)
- Github - [real-supreme](https://github.com/real-supreme)

Other forms of contact will be added later :wink:
<p style="text-align: right;">
	<a href="#table-of-contents">Top</a>
</p>
