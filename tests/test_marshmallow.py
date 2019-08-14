import json
from dataclasses import dataclass
from datetime import date, datetime

from dateutil.tz import tzoffset
from marshmallow import Schema, fields, post_load


class MarshmallowModel():
    def __init__(self,
                 str_field,
                 int_field,
                 float_field,
                 bool_field,
                 list_field,
                 date_field,
                 datetime_field,
                 nested_field
                 ):
        self.str_field = str_field
        self.int_field = int_field
        self.float_field = float_field
        self.bool_field = bool_field
        self.list_field = list_field
        self.date_field = date_field
        self.datetime_field = datetime_field
        self.nested_field = nested_field


class NestedModel():
    def __init__(self, str_field):
        self.str_field = str_field


class NestedModelSchema(Schema):
    str_field = fields.Str()

    @post_load
    def make_some_model(self, data, **kwargs):
        return NestedModel(**data)


class MarshmallowModelSchema(Schema):
    str_field = fields.Str()
    int_field = fields.Int()
    float_field = fields.Float()
    bool_field = fields.Bool()
    list_field = fields.List(fields.Str())
    date_field = fields.Date()
    datetime_field = fields.DateTime()
    nested_field = fields.Nested('NestedModelSchema')

    @post_load
    def make_some_model(self, data, **kwargs):
        return MarshmallowModel(**data)


setattr(MarshmallowModel, '__marshmallow__', MarshmallowModelSchema)


SOME_MODEL = {
    'str_field': 'test_string',
    'int_field': 1,
    'float_field': 1.5,
    'bool_field': True,
    'list_field': ['1', '2', 'str'],
    'date_field': '2019-09-08',
    'datetime_field': '2019-07-06T05:04:03+00:00',
    'nested_field': {
        'str_field': 'nested_str'
    }
}


def test_marshmallow(api):
    '''Should successfully serialize and deserialize a marshmallow model
    '''
    @api.route('/', methods=['POST'])
    def _(model: MarshmallowModel) -> MarshmallowModel:
        assert model.str_field == 'test_string'
        assert model.int_field == 1
        assert model.float_field == 1.5
        assert model.bool_field == True
        assert model.list_field == ['1', '2', 'str']
        assert model.date_field == date(2019, 9, 8)
        assert model.datetime_field == datetime(2019, 7, 6, 5, 4, 3, 0, tzoffset(None, 0))
        assert model.nested_field.str_field == 'nested_str'
        return model

    with api.flask_app.test_client() as client:
        response = client.post(json=json.dumps(SOME_MODEL))
        assert response.get_json() == SOME_MODEL
