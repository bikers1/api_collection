# -*- coding : utf-8 -*-
#################################################################################
# Author    => Albertus Restiyanto Pramayudha
# email     => xabre0010@gmail.com
# linkedin  => https://www.linkedin.com/in/albertus-restiyanto-pramayudha-470261a8/
# youtube   => https://www.youtube.com/channel/UCCtgLDIfqehJ1R8cohMeTXA
#################################################################################

{
	'name': 'API Collection',
	'summary': 'API Collection',
	'description': '''
					purchase dealer,
					purchase dealer management,
					Purchase Dealer Management
					   ''',

	'category': 'website',
	'version': '12.0.1',
	'price':  269,
	"currency": "EUR",
	'author': 'Albertus Restiyanto Pramayudha',
	'license':  'Other proprietary',
	'live_test_url':  '',
	'website': 'https://www.linkedin.com/in/albertus-restiyanto-pramayudha-470261a8/',
	'depends': [
						# 'website_purchase',
						'website',
						'purchase',
						'account',
						'cro',
						'base',
						'base_setup',
						'portal',
						'hr_attendance',
					  ],

	'data': [],
	'demo': [],
	'qweb': ['static/src/xml/*.xml'],
	'images': ['static/description/Banner_v12.gif'],
	'application': True,
	'sequence': 7,
	'pre_init_hook': '',
}
