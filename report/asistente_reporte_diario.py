# -*- encoding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError
import xlsxwriter
import base64
import io

class AsistenteReporteDiario(models.TransientModel):
    _inherit = 'l10n_gt_extra.asistente_reporte_diario'

    def print_report_excel(self):
        if not self.cuentas_id:
            raise UserError('Debe ingresar las cuentas que serán utilizadas en el reporte')

        for w in self:
            dict = {}
            dict['fecha_hasta'] = w['fecha_hasta']
            dict['fecha_desde'] = w['fecha_desde']
            dict['agrupado_por_dia'] = w['agrupado_por_dia']
            dict['cuentas_id'] =[x.id for x in w.cuentas_id]
            res = self.env['report.l10n_gt_extra.reporte_diario'].lineas(dict)

            f = io.BytesIO()
            libro = xlsxwriter.Workbook(f)
            hoja = libro.add_worksheet('Reporte')
            formato_fecha = libro.add_format({'num_format': 'dd/mm/yy'})
            formato_numero = libro.add_format({'num_format': '#,##0.00'})

            hoja.write(0, 0, 'LIBRO DIARIO')
            hoja.write(2, 0, 'NUMERO DE IDENTIFICACION TRIBUTARIA')
            hoja.write(2, 1, w.cuentas_id[0].company_id.partner_id.vat)
            hoja.write(3, 0, 'NOMBRE COMERCIAL')
            hoja.write(3, 1, w.cuentas_id[0].company_id.partner_id.name)
            hoja.write(2, 3, 'DOMICILIO FISCAL')
            hoja.write(2, 4, w.cuentas_id[0].company_id.partner_id.street)
            hoja.write(3, 3, 'REGISTRO DEL')
            hoja.write(3, 4, w.fecha_desde, formato_fecha)
            hoja.write(3, 5, 'AL')
            hoja.write(3, 6, w.fecha_hasta, formato_fecha)
            
            y = 5
            if w['agrupado_por_dia']:
                lineas = res['lineas']

                hoja.write(y, 0, 'Fecha')
                hoja.write(y, 1, 'Codigo')
                hoja.write(y, 2, 'Cuenta')
                hoja.write(y, 3, 'Debe')
                hoja.write(y, 4, 'Haber')

                for fechas in lineas:
                    y += 1
                    hoja.write(y, 0, fechas['fecha'], formato_fecha)
                    hoja.write(y, 1, fechas['asiento_contable'])
                    hoja.write(y, 2, fechas['descripcion'])
                    for cuentas in fechas['cuentas']:
                        y += 1
                        hoja.write(y, 1, cuentas['codigo'])
                        hoja.write(y, 2, cuentas['cuenta'])
                        hoja.write(y, 3, cuentas['debe'], formato_numero)
                        hoja.write(y, 4, cuentas['haber'], formato_numero)
                    y += 1
                    hoja.write(y, 3, fechas['total_debe'], formato_numero)
                    hoja.write(y, 4, fechas['total_haber'], formato_numero)

            else:
                lineas = res['lineas']
                totales = res['totales']

                hoja.write(y, 0, 'Codigo')
                hoja.write(y, 1, 'Cuenta')
                hoja.write(y, 2, 'Debe')
                hoja.write(y, 3, 'Haber')

                for linea in lineas:
                    y += 1

                    hoja.write(y, 0, linea['codigo'])
                    hoja.write(y, 1, linea['cuenta'])
                    hoja.write(y, 2, linea['debe'], formato_numero)
                    hoja.write(y, 3, linea['haber'], formato_numero)

                y += 1
                hoja.write(y, 1, 'Totales')
                hoja.write(y, 2, totales['debe'], formato_numero)
                hoja.write(y, 3, totales['haber'], formato_numero)

            libro.close()
            datos = base64.b64encode(f.getvalue())
            self.write({'archivo':datos, 'name':'libro_diario.xlsx'})

        return {
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'l10n_gt_extra.asistente_reporte_diario',
            'res_id': self.id,
            'view_id': False,
            'type': 'ir.actions.act_window',
            'target': 'new',
        }
