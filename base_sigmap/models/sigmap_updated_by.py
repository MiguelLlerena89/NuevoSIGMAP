from odoo import api, fields, models, _

class SigmapUpdatedBy(models.Model):
    _name = 'sigmap.updated.by'
    _description = _( 'Update By')

    # Actualizado por    
    updated_by = fields.Char(
        string=_('Updated by'),
        compute='_compute_updated_by',
        store=True,
        copy=False)

    def _compute_updated_by(self):
        for res in self:
            wr_user = ''
            wr_date = ''
            try:
                wr_user = res.write_uid
                wr_date = res.write_date
            except Exception as err:
                print(err)

            res.updated_by = f'{wr_user} [{wr_date}]'
