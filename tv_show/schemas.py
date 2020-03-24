from marshmallow import Schema, fields


class TvShow(Schema):
    name = fields.String(required=True)
    season_number = fields.Int(required=True)
    episode_number = fields.Int(required=True)
    looked = fields.Bool(required=True)
