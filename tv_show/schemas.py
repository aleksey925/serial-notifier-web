from marshmallow import Schema, fields


class TvShow(Schema):
    tv_shows = fields.Dict(
        keys=fields.Str,
        values=fields.Dict(keys=fields.Str, values=fields.List(fields.Int))
    )
