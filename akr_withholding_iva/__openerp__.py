{
    "name": "Retenciones de IVA AKR 58 C.A",
    "version": "1.1",
    "author" : "Luis Torres",
    "category": "Retenciones",
    "description": """
     Este modulo contiene las adaptaciones de los modulos de retenciones fiscales de Iva para AKR 58, C.A
    """,
    'images': [],
    'depends': ['account','l10n_ve_withholding','l10n_ve_withholding_iva','purchase'],
    'data': [
            'report/withholding_vat_report.xml',
            'view/partner_view.xml',
            'view/account_tax_view.xml',
            ],
    'init_xml': [],
    'update_xml': [],
    'demo_xml': [],
    'test': [],
    'installable': True,
    'active': True,
    'auto_install': False,
}
