import os
import pytest
import pkg_resources
from uuid import uuid4
from pytest import raises
from roconfiguration import Configuration, ConfigurationOverrideError


class TestConfiguration:

    def test_empty_constructor(self):
        config = Configuration()

        assert config is not None

    def test_mapping(self):
        config = Configuration({'foo': True})

        assert config.foo is True

    def test_read_dictionary_notation(self):
        # bad practice, but still supported:
        config = Configuration({'foo.power': True, 'foo': {'power': False}})

        assert config['foo.power'] is True
        assert config.foo.power is False

    def test_missing_key_error(self):
        config = Configuration({'foo': True})

        with pytest.raises(KeyError):
            print(config.a)

    def test_missing_file_error(self):
        config = Configuration()

        filepath = pkg_resources.resource_filename(__name__, './not_existing.foo')

        assert not os.path.exists(filepath)

        with pytest.raises(FileNotFoundError):
            config.add_ini_file(filepath)

        with pytest.raises(FileNotFoundError):
            config.add_json_file(filepath)

        with pytest.raises(FileNotFoundError):
            config.add_yaml_file(filepath)

    def test_optional_ini_does_not_throw(self):
        config = Configuration()

        not_existing_file = f'{uuid4()}.ini'

        config.add_ini_file(not_existing_file, optional=True)

        assert True is True

    def test_optional_json_does_not_throw(self):
        config = Configuration()

        not_existing_file = f'{uuid4()}.json'

        config.add_json_file(not_existing_file, optional=True)

        assert True is True

    def test_optional_yaml_does_not_throw(self):
        config = Configuration()

        not_existing_file = f'{uuid4()}.yaml'

        config.add_yaml_file(not_existing_file, optional=True)

        assert True is True

    def test_yaml_can_use_full_loader(self):
        filepath = pkg_resources.resource_filename(__name__, './yaml_example_01.yaml')

        config = Configuration()
        config.add_yaml_file(filepath, safe_load=False)

        assert config.host == 'localhost'
        assert config.port == 44555
        assert config.jwt_issuer == 'https://example.org'
        assert config.jwt_audience == 'https://example.org'
        assert config.jwt_algorithms == ['HS256']

    def test_mapping_adding(self):
        config = Configuration({'foo': True})

        config.add_map({'hello': 'world'})

        assert config.foo is True
        assert config.hello == 'world'

    def test_mapping_overriding(self):
        config = Configuration({'foo': True})

        config.add_map({'foo': 'world'})

        assert config.foo == 'world'

    def test_nested_overriding(self):
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

        config.add_value('a:d:g', 6)

        assert config.a.d.g == 6

        config.add_value('x:y:z', 7)

        assert config.x.y.z == 7

    def test_reading_nested_list_values(self):
        config = Configuration({'b2c': [
            {'tenant': '1'},
            {'tenant': '2'},
            {'tenant': '3'}
        ]})

        assert config.b2c[0].tenant == '1'
        assert config.b2c[1].tenant == '2'
        assert config.b2c[2].tenant == '3'

    def test_overriding_nested_list_values(self):
        config = Configuration({'b2c': [
            {'tenant': '1'},
            {'tenant': '2'},
            {'tenant': '3'}
        ]})

        config.add_value('b2c:1:tenant', '4')

        assert config.b2c[0].tenant == '1'
        assert config.b2c[1].tenant == '4'
        assert config.b2c[2].tenant == '3'

    def test_overriding_nested_list_values_raises_for_invalid_key(self):
        config = Configuration({'b2c': [
            {'tenant': '1'},
            {'tenant': '2'},
            {'tenant': '3'}
        ]})

        with raises(ConfigurationOverrideError):
            config.add_value('b2c:foo:tenant', '4')

    def test_overriding_nested_list_item(self):
        config = Configuration({'ids': [1, 2, 3, 4, 5]})

        assert config.ids[0] == 1
        assert config.ids[1] == 2
        assert config.ids[2] == 3

        config.add_value('ids:1', 6)

        assert config.ids[0] == 1
        assert config.ids[1] == 6
        assert config.ids[2] == 3

    def test_invalid_overriding_nested_list_item(self):
        config = Configuration({'ids': [1, 2, 3, 4, 5]})

        with pytest.raises(ConfigurationOverrideError):
            config.add_value('ids:1:foo', 6)

    def test_add_environmental_variables(self):
        unique_value = 'hopefully_there_is_no_env_variable_with_such_name'

        # arrange
        os.environ[unique_value] = 'Hello, World'

        config = Configuration()

        with pytest.raises(KeyError):
            print(config.hopefully_there_is_no_env_variable_with_such_name)

        config.add_environmental_variables()

        assert config.hopefully_there_is_no_env_variable_with_such_name == 'Hello, World'

    def test_add_environmental_variables_with_filter(self):
        # arrange
        os.environ['app_foo'] = '1'
        os.environ['app_ofo'] = '2'
        os.environ['app_oof'] = '3'
        os.environ['nope'] = '4'

        config = Configuration()
        config.add_environmental_variables('app_')

        assert config.app_foo == '1'
        assert config.app_ofo == '2'
        assert config.app_oof == '3'

        with pytest.raises(KeyError):
            print(config.nope)

    def test_override_with_environmental_variables(self):
        config = Configuration({'foo': 10, 'ufo': 20})

        assert config.foo == 10
        assert config.ufo == 20

        os.environ['foo'] = 'Something else'

        config.add_environmental_variables()

        assert config.foo == 'Something else'
        assert config.ufo == 20

    def test_dict_property_name(self):
        config = Configuration({'items': 200})

        assert config.items == 200

    def test_list_item_as_configuration(self):
        config = Configuration({'items': [
            {'id': '1'},
            {'id': '2'}
        ]})

        first_item = config.items[0]
        assert isinstance(first_item, Configuration)
        assert first_item.id == '1'

    def test_list_of_values(self):
        config = Configuration({'items': [
            {'id': '1'},
            {'id': '2'}
        ]})

        assert len(config.items) == 2
        assert config.items[0].id == '1'
        assert config.items[1].id == '2'

    def test_add_ini_settings(self):
        config = Configuration()

        ini_settings = """[DEFAULT]
server_alive_interval = 45
compression = yes
compression_level = 9
forward_x11 = yes
utf8_check = cześć

[example]
user = hg

[another]
port = 50022
forward_x11 = no"""

        config.add_ini(ini_settings)

        # NB: support 'DEFAULT' magic section handled by built-in ConfigParser
        assert config.example.user == 'hg'
        assert config.example.server_alive_interval == '45'
        assert config.example.compression == 'yes'
        assert config.example.forward_x11 == 'yes'
        assert config.example.utf8_check == 'cześć'

        assert config.another.server_alive_interval == '45'
        assert config.another.compression == 'yes'
        assert config.another.port == '50022'
        assert config.another.forward_x11 == 'no'

    def test_add_ini_file(self):
        filepath = pkg_resources.resource_filename(__name__, './ini_example_01.ini')

        config = Configuration()
        config.add_ini_file(filepath)

        assert config.a.port == '8080'
        assert config.a.something == 'hello'
        assert config.b.port == '50022'
        assert config.b.something == 'world'

    def test_add_json_file(self):
        filepath = pkg_resources.resource_filename(__name__, './json_example_01.json')

        config = Configuration()
        config.add_json_file(filepath)

        assert config.ApplicationInsights.InstrumentationKey == '742dc2e1-3f6f-447a-b710-6bf61d6e8a3c'
        assert config.Authentication.B2C[0].IssuerName == 'example'
        assert config.Logging.IncludeScopes is False

        for b2c_conf in config.Authentication.B2C:
            assert b2c_conf.IssuerName.startswith('example')

    def test_add_yaml_file(self):
        filepath = pkg_resources.resource_filename(__name__, './yaml_example_01.yaml')

        config = Configuration()
        config.add_yaml_file(filepath)

        assert config.host == 'localhost'
        assert config.port == 44555
        assert config.jwt_issuer == 'https://example.org'
        assert config.jwt_audience == 'https://example.org'
        assert config.jwt_algorithms == ['HS256']

    def test_add_yaml2_file(self):
        filepath = pkg_resources.resource_filename(__name__, './yaml_example_02.yaml')

        config = Configuration()
        config.add_yaml_file(filepath)

        assert config.foo[0].shares == -75.088
        assert config.foo[0].date == '11/27/2015'
        assert config.foo[1].shares == 75.088
        assert config.services.encryption.key == 'SECRET_KEY'
        assert config.services.images.processor.type == 'local'

    @pytest.mark.parametrize('keyword', [
        ('for',),
        ('del',)
    ])
    def test_keywords_handling(self, keyword):
        config = Configuration({keyword: 1})
        assert config[keyword] == 1


@pytest.mark.parametrize('source,key,value,expected', [
    ({}, 'a', 100, {'a': 100}),
    ({}, 'message', 'Hello World', {'message': 'Hello World'}),
    ({}, 'a:b', 'Hello World', {'a': {'b': 'Hello World'}}),
    ({}, 'a:b:c', 'Hello World', {'a': {'b': {'c': 'Hello World'}}}),
    ({'a': ['Source']}, 'a:0', 'Hello World', {'a': ['Hello World']}),
    ({'a': {'b': ['Source']}}, 'a:b:0', 'Hello World', {'a': {'b': ['Hello World']}}),
])
def test_add_value(source, key, value, expected):
    config = Configuration(source)

    config.add_value(key, value)

    assert config.values == expected


@pytest.mark.parametrize('source,key,value', [
    ({'a': []}, 'a:0', 'Hello World'),
    ({'a': ['Hello World']}, 'a:c', 'Hello World'),
    ({'a': 'Hello'}, 'a:b:c', 'Hello World')
])
def test_apply_key_value_raises_for_invalid_overrides(source, key, value):
    config = Configuration(source)

    with raises(ConfigurationOverrideError):
        config.add_value(key, value)



