[![Build status](https://robertoprevato.visualstudio.com/roconfiguration/_apis/build/status/roconfiguration-CI)](https://robertoprevato.visualstudio.com/roconfiguration/_build/latest?definitionId=10)

# Python configuration utilities
Implementation of key-value pair based configuration for Python applications.

**Features:**
* support for most common sources of application settings
* support for overriding settings in sequence
* support for nested structures and lists, using attribute notation
* strategy to use environment specific settings

This library is freely inspired by .NET Core `Microsoft.Extensions.Configuration` namespace and its pleasant design (_ref. [MSDN documentation](https://docs.microsoft.com/en-us/aspnet/core/fundamentals/configuration/?view=aspnetcore-2.1), [Microsoft Extensions Configuration Deep Dive](https://www.paraesthesia.com/archive/2018/06/20/microsoft-extensions-configuration-deep-dive/)_).

The main class is influenced by Luciano Ramalho's example of 
JSON structure explorer using attribute notation, in his book [Fluent Python](http://shop.oreilly.com/product/0636920032519.do).

## Supported sources:
* **yaml** files
* **json** files
* **ini** files
* environmental variables
* dictionaries
* keys and values

## Installation
```bash
pip install roconfiguration
```

# Examples

### YAML file and environmental variables
In this example, configuration will be comprised of anything inside a file `settings.yaml` and environmental variables. Settings are applied in order, so environmental variables with matching name override values from the `yaml` file.


```python
from roconfiguration import Configuration

config = Configuration()

config.add_yaml_file('settings.yaml')

config.add_environmental_variables()
```

### YAML file, optional file by environment
In this example, if an environmental variable with name `APP_ENVIRONMENT` and value `dev` exists, and a configuration file with name `settings.dev.yaml` is present, it is read to override values configured in `settings.yaml` file. 
```python
import os
from roconfiguration import Configuration

environment_name = os.environ['APP_ENVIRONMENT']

config = Configuration()

config.add_yaml_file('settings.yaml')
config.add_yaml_file(f'settings.{environment_name}.yaml', optional=True)

config.add_environmental_variables()
```

### Filtering environmental variables by prefix
```python
import os
from roconfiguration import Configuration

config = Configuration()

# will read only environmental variables
# starting with 'APP_', case insensitively
config.add_environmental_variables('APP_')
```

### Ini files
Ini files are parsed using the built-in `configparser` module, therefore support `[DEFAULT]` section; all values are kept as strings.
```python
from roconfiguration import Configuration

config = Configuration()

config.add_ini_file('settings.ini')
```

### JSON files
JSON files are parsed using the built-in `json` module.
```python
from roconfiguration import Configuration

config = Configuration()

config.add_json_file('settings.json')
```

### Dictionaries
```python
from roconfiguration import Configuration

config = Configuration({'host': 'localhost', 'port': 8080})

config.add_map({
    'hello': 'world',
    'example': [{
      'id': 1
    }, {
      'id': 2
    }]
})

assert config.host == 'localhost'
assert config.port == 8080
assert config.hello == 'world'
assert config.example[0].id == 1
assert config.example[1].id == 2
```

### Keys and values
```python
from roconfiguration import Configuration

config = Configuration({'host': 'localhost', 'port': 8080})

config.add_value('port', 44555)

assert config.host == 'localhost'
assert config.port == 44555
```

### Overriding nested values
```python
config = Configuration({'a': {
    'b': 1,
    'c': 2,
    'd': {
        'e': 3,
        'f': 4
    }
}})

assert config.a.b == 1
assert config.a.d.e == 3
assert config.a.d.f == 4

config.add_value('a:d:e', 5)

assert config.a.d.e == 5
assert config.a.d.f == 4
```

### Overriding nested values using env variables
```python
config = Configuration({'a': {
    'b': 1,
    'c': 2,
    'd': {
        'e': 3,
        'f': 4
    }
}})

assert config.a.b == 1
assert config.a.d.e == 3
assert config.a.d.f == 4

# NB: if an env variable such as:
# a:d:e=5
# or...
# a__d__e=5
#
# is defined, it overrides the value  from the dictionary

config.add_environmental_variables()

assert config.a.d.e == 5
```

### Overriding values in list items using env variables
```python
config = Configuration({'b2c': [
    {'tenant': '1'},
    {'tenant': '2'},
    {'tenant': '3'}
]})

config.add_value('b2c:1:tenant', '4')

assert config.b2c[0].tenant == '1'
assert config.b2c[1].tenant == '4'
assert config.b2c[2].tenant == '3'
```

---

# Develop and run tests locally
```bash
pip install -r dev_requirements.txt

# run tests using automatic discovery:
pytest
```
