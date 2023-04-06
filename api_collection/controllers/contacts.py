# -*- coding : utf-8 -*-
#################################################################################
# Author    => Albertus Restiyanto Pramayudha
# email     => xabre0010@gmail.com
# linkedin  => https://www.linkedin.com/in/albertus-restiyanto-pramayudha-470261a8/
# youtube   => https://www.youtube.com/channel/UCCtgLDIfqehJ1R8cohMeTXA
#################################################################################

import json
import math
import logging
import requests

from odoo import http, _, exceptions
from odoo.http import request
from odoo.addons.web.controllers.main import Home

from .serializers import Serializer
from .exceptions import QueryFormatError
import datetime

def error_response(error, msg):
    return {
        "jsonrpc": "2.0",
        "id": None,
        "error": {
            "code": 200,
            "message": msg,
            "data": {
                "name": str(error),
                "debug": "",
                "message": msg,
                "arguments": list(error.args),
                "exception_type": type(error).__name__
            }
        }
    }


class APiCollections(Home):
    def make_json_response(self, data, headers=None, cookies=None):
        data = json.dumps(data)
        if headers is None:
            headers = {}
        headers["Content-Type"] = "application/json"
        return request.make_response(data, headers=headers, cookies=cookies)

    @http.route('/token',type='json', auth='none', methods=["GET"], csrf=False)
    def authenticate(self, *args, **post):
        ir_config_model = request.env['ir.config_parameter']
        password =''
        db =''
        login = ''
        login = ir_config_model.sudo().get_param("api_server_user")
        password = ir_config_model.sudo().get_param("api_server_password")
        db = ir_config_model.sudo().get_param("api_server_database")
        url_root = request.httprequest.url_root
        AUTH_URL = f"{url_root}web/session/authenticate/"

        headers = {'Content-type': 'application/json'}

        data = {
            "jsonrpc": "2.0",
            "params": {
                "login": login,
                "password": password,
                "db": db
            }
        }

        res = requests.post(
            AUTH_URL,
            data=json.dumps(data),
            headers=headers
        )

        try:
            session_id = res.cookies["session_id"]
            user = json.loads(res.text)
            user["result"]["session_id"] = session_id
        except Exception:
            return "Invalid credentials."
        return self.make_json_response(user["result"]["session_id"])


    @http.route('/api/product',type='json', auth='user',methods=['GET'])
    def get_master_product_data(self, **params):
        try:
            yesterday = datetime.datetime.now() - datetime.timedelta(days=1)
            yesterday_beginning = datetime.datetime(yesterday.year, yesterday.month, yesterday.day, 0, 0, 0, 0)
            yb = yesterday_beginning.strftime("%Y-%m-%d %I:%M:%S")
            today = datetime.datetime.now()
            today_beginning = datetime.datetime(today.year, today.month, today.day, 0, 0, 0, 0)
            tb = today_beginning.strftime("%Y-%m-%d %I:%M:%S")
            if "write_date" in params:
                tglawal = '%s %s' % (params['write_date'],'00:00:00')
                tglminta1 = datetime.datetime.strptime(tglawal, '%Y-%m-%d %H:%M:%S')
                tglakhir = '%s %s' % (params['write_date'],'23:59:59')
                tglminta2 = datetime.datetime.strptime(tglakhir, '%Y-%m-%d %H:%M:%S')
                records = request.env['product.product'].search([('state','=','approve'),('write_date','>=',tglminta1),('write_date','<',tglminta2)])
            elif "limit" in params:
                mylimit = int(params['limit'])
                records = request.env['product.product'].search(
                    [('state','=','approve')], limit=mylimit)
            elif "display_name" in params:
                mytemp = request.env['product.template'].search([])
                myprod = mytemp.filtered(lambda rr: rr.display_name == params['display_name'])
                records = request.env['product.product'].search([('product_tmpl_id','=', myprod.id)])
            elif "id" in params:
                mytemp = request.env['product.product'].browse(int(params['id']))
                records = mytemp.filtered(lambda k: k.state == 'approve',)
            elif "name" in params:
                mytemp = request.env['product.template'].search([('name','=',params['name'])])
                records = request.env['product.product'].search([('state','=','approve'),('product_tmpl_id','=',mytemp.id)])
            else:
                records = request.env['product.product'].search([('product_tmpl_id.state_product','=','approve'),('product_tmpl_id.active','=',True)])
        except KeyError as e:
            msg = "The model `%s` does not exist." % 'product.product'
            return self.make_json_response(msg)
        query = "{id,default_code,core_item,company_id,responsible_id,name,product_brand_id,sale_ok,purchase_ok,list_price,standard_price,uom_id,uom_po_id,categ_id,type,write_date,barcode,qty_available}"
        orders = ""
        prev_page = None
        next_page = None
        total_page_number = 1
        current_page = 1

        if "data_count" in params:
            page_size = int(params["data_count"])
            count = len(records)
            total_page_number = math.ceil(count / page_size)
        else:
            page_size = len(records)
            total_page_number = 1

        if "page" in params:
            current_page = int(params["page"])
        else:
            current_page = 1
        start = page_size*(current_page-1)
        stop = current_page*page_size
        records = records[start:stop]
        next_page = current_page+1 \
            if 0 < current_page + 1 <= total_page_number \
            else None
        prev_page = current_page-1 \
            if 0 < current_page - 1 <= total_page_number \
            else None

        try:
            serializer = Serializer(records, query, many=True)
            data = serializer.data
        except (SyntaxError, QueryFormatError) as e:
            res = error_response(e, e.msg)
            return self.make_json_response(res)
        res = {
            "count": len(records),
            "prev": prev_page,
            "current": current_page,
            "next": next_page,
            "total_pages": total_page_number,
            "product_core": data
        }

        return self.make_json_response(res)

    @http.route('/api/attendence',type='http', auth='user',methods=['GET'])
    def get_master_attendent(self, **params):
        print('test jalan')
        return
    @http.route('/api/contact',type='http', auth='user',methods=['GET'])
    def get_master_contacts_data(self, **params):
        try:
            yesterday = datetime.datetime.now() - datetime.timedelta(days=1)
            yesterday_beginning = datetime.datetime(yesterday.year, yesterday.month, yesterday.day, 0, 0, 0, 0)
            yb = yesterday_beginning.strftime("%Y-%m-%d %I:%M:%S")
            today = datetime.datetime.now()
            today_beginning = datetime.datetime(today.year, today.month, today.day, 0, 0, 0, 0)
            tb = today_beginning.strftime("%Y-%m-%d %I:%M:%S")
            if "write_date" in params:
                tglawal ='%s %s' %(params['write_date'],'00:00:00')
                tglminta1 = datetime.datetime.strptime(tglawal, '%Y-%m-%d %H:%M:%S')
                tglakhir = '%s %s' %(params['write_date'],'23:59:59')
                tglminta2 = datetime.datetime.strptime(tglakhir, '%Y-%m-%d %H:%M:%S')
                records = request.env['res.partner'].search([('write_date','>=',tglminta1),('write_date','<',tglminta2)])
            elif "limit" in params:
                mylimit = int(params['limit'])
                records = request.env['res.partner'].search(
                    [('state','=','approve')], limit=mylimit)
            elif "id" in params:
                myprod = request.env['res.partner'].browse(int(params['id']))
                records = myprod
            elif "name" in params:
                mytemp = request.env['res.partner'].search([('name','ilike',params['name'])])
                records = mytemp
            else:
                records = request.env['res.partner'].search(
                    [])
        except KeyError as e:
            msg = "The model `%s` does not exist." % 'res.partner'
            return self.make_json_response(msg)
        query = "{id,name,jenis_partner,street_name,street2,kota_id}"
        orders = ""
        prev_page = None
        next_page = None
        total_page_number = 1
        current_page = 1

        if "data_count" in params:
            page_size = int(params["data_count"])
            count = len(records)
            total_page_number = math.ceil(count / page_size)
        else:
            page_size = len(records)
            total_page_number = 1

        if "page" in params:
            current_page = int(params["page"])
        else:
            current_page = 1
        start = page_size*(current_page-1)
        stop = current_page*page_size
        records = records[start:stop]
        next_page = current_page+1 \
            if 0 < current_page + 1 <= total_page_number \
            else None
        prev_page = current_page-1 \
            if 0 < current_page - 1 <= total_page_number \
            else None

        try:
            serializer = Serializer(records, query, many=True)
            data = serializer.data
        except (SyntaxError, QueryFormatError) as e:
            res = error_response(e, e.msg)
            return self.make_json_response(res)
        res = {
            "count": len(records),
            "prev": prev_page,
            "current": current_page,
            "next": next_page,
            "total_pages": total_page_number,
            "product_core": data
        }

        return self.make_json_response(res)
    @http.route('/api/product-template',type='http', auth='user',methods=['GET'])
    def get_master_product_template_data(self, **params):
        try:
            yesterday = datetime.datetime.now() - datetime.timedelta(days=1)
            yesterday_beginning = datetime.datetime(yesterday.year, yesterday.month, yesterday.day, 0, 0, 0, 0)
            yb = yesterday_beginning.strftime("%Y-%m-%d %I:%M:%S")
            today = datetime.datetime.now()
            today_beginning = datetime.datetime(today.year, today.month, today.day, 0, 0, 0, 0)
            tb = today_beginning.strftime("%Y-%m-%d %I:%M:%S")
            if "write_date" in params:
                tglawal ='%s %s' %(params['write_date'],'00:00:00')
                tglminta1 = datetime.datetime.strptime(tglawal, '%Y-%m-%d %H:%M:%S')
                tglakhir = '%s %s' %(params['write_date'],'23:59:59')
                tglminta2 = datetime.datetime.strptime(tglakhir, '%Y-%m-%d %H:%M:%S')
                records = request.env['product.product'].search([('state','=','approve'),('write_date','>=',tglminta1),('write_date','<',tglminta2)])
            elif "limit" in params:
                mylimit = int(params['limit'])
                records = request.env['product.product'].search(
                    [('state','=','approve')], limit=mylimit)
            elif "id" in params:
                myprod = request.env['product.product'].browse(int(params['id']))
                records = myprod.product_tmpl_id
            elif "name" in params:
                mytemp = request.env['product.template'].search([('name','=',params['name'])])
                records = request.env['product.product'].search([('state','=','approve'),('product_tmpl_id','=',mytemp.id)])
            else:
                records = request.env['product.product'].search(
                    [('state','=','approve')])
        except KeyError as e:
            msg = "The model `%s` does not exist." % 'product.template'
            return self.make_json_response(msg)
        query = "{id,display_name}"
        orders = ""
        prev_page = None
        next_page = None
        total_page_number = 1
        current_page = 1

        if "data_count" in params:
            page_size = int(params["data_count"])
            count = len(records)
            total_page_number = math.ceil(count / page_size)
        else:
            page_size = len(records)
            total_page_number = 1

        if "page" in params:
            current_page = int(params["page"])
        else:
            current_page = 1
        start = page_size*(current_page-1)
        stop = current_page*page_size
        records = records[start:stop]
        next_page = current_page+1 \
            if 0 < current_page + 1 <= total_page_number \
            else None
        prev_page = current_page-1 \
            if 0 < current_page - 1 <= total_page_number \
            else None

        try:
            serializer = Serializer(records, query, many=True)
            data = serializer.data
        except (SyntaxError, QueryFormatError) as e:
            res = error_response(e, e.msg)
            return self.make_json_response(res)
        res = {
            "count": len(records),
            "prev": prev_page,
            "current": current_page,
            "next": next_page,
            "total_pages": total_page_number,
            "product_core": data
        }

        return self.make_json_response(res)

    @http.route('/api/product-category',type='http', auth='user',methods=['GET'])
    def get_master_category_data(self, **params):
        try:
            yesterday = datetime.datetime.now() - datetime.timedelta(days=1)
            yesterday_beginning = datetime.datetime(yesterday.year, yesterday.month, yesterday.day, 0, 0, 0, 0)
            yb = yesterday_beginning.strftime("%Y-%m-%d %I:%M:%S")
            today = datetime.datetime.now()
            today_beginning = datetime.datetime(today.year, today.month, today.day, 0, 0, 0, 0)
            tb = today_beginning.strftime("%Y-%m-%d %I:%M:%S")
            if "write_date" in params:
                tglawal ='%s %s' %(params['write_date'],'00:00:00')
                tglminta1 = datetime.datetime.strptime(tglawal, '%Y-%m-%d %H:%M:%S')
                tglakhir = '%s %s' %(params['write_date'],'23:59:59')
                tglminta2 = datetime.datetime.strptime(tglakhir, '%Y-%m-%d %H:%M:%S')
                records = request.env['product.category'].search([('write_date','>=',tglminta1),('write_date','<',tglminta2)])
            elif "complete_name" in params:
                records = request.env['product.category'].search(
                    [('complete_name','=', params['complete_name'])])
            else:
                records = request.env['product.category'].search(
                    [])
        except KeyError as e:
            msg = "The model `%s` does not exist." % 'product.product'
            return self.make_json_response(msg)
        query = "{*}"
        orders = ""
        prev_page = None
        next_page = None
        total_page_number = 1
        current_page = 1

        if "data_count" in params:
            page_size = int(params["data_count"])
            count = len(records)
            total_page_number = math.ceil(count / page_size)
        else:
            page_size = len(records)
            total_page_number = 1

        if "page" in params:
            current_page = int(params["page"])
        else:
            current_page = 1
        start = page_size*(current_page-1)
        stop = current_page*page_size
        records = records[start:stop]
        next_page = current_page+1 \
            if 0 < current_page + 1 <= total_page_number \
            else None
        prev_page = current_page-1 \
            if 0 < current_page - 1 <= total_page_number \
            else None

        try:
            serializer = Serializer(records, query, many=True)
            data = serializer.data
        except (SyntaxError, QueryFormatError) as e:
            res = error_response(e, e.msg)
            return self.make_json_response(res)
        res = {
            "count": len(records),
            "prev": prev_page,
            "current": current_page,
            "next": next_page,
            "total_pages": total_page_number,
            "product_category_core": data
        }

        return self.make_json_response(res)


    @http.route('/api/stock-warehouse',type='http', auth='user',methods=['GET'])
    def get_master_warehouses_data(self, **params):
        try:
            yesterday = datetime.datetime.now() - datetime.timedelta(days=1)
            yesterday_beginning = datetime.datetime(yesterday.year, yesterday.month, yesterday.day, 0, 0, 0, 0)
            yb = yesterday_beginning.strftime("%Y-%m-%d %I:%M:%S")
            today = datetime.datetime.now()
            today_beginning = datetime.datetime(today.year, today.month, today.day, 0, 0, 0, 0)
            tb = today_beginning.strftime("%Y-%m-%d %I:%M:%S")
            if "write_date" in params:
                tglawal ='%s %s' %(params['write_date'],'00:00:00')
                tglminta1 = datetime.datetime.strptime(tglawal, '%Y-%m-%d %H:%M:%S')
                tglakhir = '%s %s' %(params['write_date'],'23:59:59')
                tglminta2 = datetime.datetime.strptime(tglakhir, '%Y-%m-%d %H:%M:%S')
                records = request.env['stock.warehouse'].search([('write_date','>=',tglminta1),('write_date','<',tglminta2)])
            elif "name" in params and "company_id" in params:
                records = request.env['stock.warehouse'].search(
                    [('name','=', params['name']),('company_id.name','=',params['company_id'])])
            elif "company_id" in params:
                records = request.env['stock.warehouse'].search(
                    [('company_id.name','ilike', params['company_id'])])
            else:
                records = request.env['stock.warehouse'].search(
                    [])
        except KeyError as e:
            msg = "The model `%s` does not exist." % 'product.product'
            return self.make_json_response(msg)
        query = "{*}"
        orders = ""
        prev_page = None
        next_page = None
        total_page_number = 1
        current_page = 1

        if "data_count" in params:
            page_size = int(params["data_count"])
            count = len(records)
            total_page_number = math.ceil(count / page_size)
        else:
            page_size = len(records)
            total_page_number = 1

        if "page" in params:
            current_page = int(params["page"])
        else:
            current_page = 1
        start = page_size*(current_page-1)
        stop = current_page*page_size
        records = records[start:stop]
        next_page = current_page+1 \
            if 0 < current_page + 1 <= total_page_number \
            else None
        prev_page = current_page-1 \
            if 0 < current_page - 1 <= total_page_number \
            else None

        try:
            serializer = Serializer(records, query, many=True)
            data = serializer.data
        except (SyntaxError, QueryFormatError) as e:
            res = error_response(e, e.msg)
            return self.make_json_response(res)
        res = {
            "count": len(records),
            "prev": prev_page,
            "current": current_page,
            "next": next_page,
            "total_pages": total_page_number,
            "stock_warehouse": data
        }

        return self.make_json_response(res)


    @http.route('/api/stock-location',type='http', auth='user',methods=['GET'])
    def get_stock_location_datas(self, **params):
        try:
            yesterday = datetime.datetime.now() - datetime.timedelta(days=1)
            yesterday_beginning = datetime.datetime(yesterday.year, yesterday.month, yesterday.day, 0, 0, 0, 0)
            yb = yesterday_beginning.strftime("%Y-%m-%d %I:%M:%S")
            today = datetime.datetime.now()
            today_beginning = datetime.datetime(today.year, today.month, today.day, 0, 0, 0, 0)
            tb = today_beginning.strftime("%Y-%m-%d %I:%M:%S")
            if "write_date" in params:
                tglawal ='%s %s' %(params['write_date'],'00:00:00')
                tglminta1 = datetime.datetime.strptime(tglawal, '%Y-%m-%d %H:%M:%S')
                tglakhir = '%s %s' %(params['write_date'],'23:59:59')
                tglminta2 = datetime.datetime.strptime(tglakhir, '%Y-%m-%d %H:%M:%S')
                records = request.env['stock.location'].search([('write_date','>=',tglminta1),('write_date','<',tglminta2)])
            elif "complete_name" in params and "company_id" in params:
                records = request.env['stock.location'].search([('complete_name','ilike',params['complete_name']),('company_id.name','ilike',params['company_id'])])
            elif "company_id" in params:
                records = request.env['stock.location'].search(
                    [('company_id.name','ilike', params['company_id'])])
            else:
                records = request.env['stock.location'].search(
                    [])
        except KeyError as e:
            msg = "The model `%s` does not exist." % 'stock.location'
            return self.make_json_response(msg)
        query = "{*}"
        orders = ""
        prev_page = None
        next_page = None
        total_page_number = 1
        current_page = 1

        if "data_count" in params:
            page_size = int(params["data_count"])
            count = len(records)
            total_page_number = math.ceil(count / page_size)
        else:
            page_size = len(records)
            total_page_number = 1

        if "page" in params:
            current_page = int(params["page"])
        else:
            current_page = 1
        start = page_size*(current_page-1)
        stop = current_page*page_size
        records = records[start:stop]
        next_page = current_page+1 \
            if 0 < current_page + 1 <= total_page_number \
            else None
        prev_page = current_page-1 \
            if 0 < current_page - 1 <= total_page_number \
            else None

        try:
            serializer = Serializer(records, query, many=True)
            data = serializer.data
        except (SyntaxError, QueryFormatError) as e:
            res = error_response(e, e.msg)
            return self.make_json_response(res)
        res = {
            "count": len(records),
            "prev": prev_page,
            "current": current_page,
            "next": next_page,
            "total_pages": total_page_number,
            "stock_location": data
        }

        return self.make_json_response(res)


    @http.route('/api/stock-operation-type',type='http', auth='user',methods=['GET'])
    def get_model_op_type_data(self, **params):
        try:
            yesterday = datetime.datetime.now() - datetime.timedelta(days=1)
            yesterday_beginning = datetime.datetime(yesterday.year, yesterday.month, yesterday.day, 0, 0, 0, 0)
            yb = yesterday_beginning.strftime("%Y-%m-%d %I:%M:%S")
            today = datetime.datetime.now()
            today_beginning = datetime.datetime(today.year, today.month, today.day, 0, 0, 0, 0)
            tb = today_beginning.strftime("%Y-%m-%d %I:%M:%S")
            if "write_date" in params:
                tglawal ='%s %s' %(params['write_date'],'00:00:00')
                tglminta1 = datetime.datetime.strptime(tglawal, '%Y-%m-%d %H:%M:%S')
                tglakhir = '%s %s' %(params['write_date'],'23:59:59')
                tglminta2 = datetime.datetime.strptime(tglakhir, '%Y-%m-%d %H:%M:%S')
                records = request.env['stock.picking.type'].search([('write_date','>=',tglminta1),('write_date','<',tglminta2)])
            elif "int_type_id" in params and "company_id" in params:
                domain = ['|', ('name', 'ilike', params['int_type_id']),
                          ('warehouse_id.name', 'ilike', params['int_type_id']),('company_id.name','ilike',params['company_id'])]
                records = request.env['stock.picking.type'].search(domain)
            elif "company_id" in params:
                records = request.env['stock.picking.type'].search(
                    [('company_id.name','ilike', params['company_id'])])
            else:
                records = request.env['stock.picking.type'].search(
                    [])
        except KeyError as e:
            msg = "The model `%s` does not exist." % 'product.product'
            return self.make_json_response(msg)
        query = "{*}"
        orders = ""
        prev_page = None
        next_page = None
        total_page_number = 1
        current_page = 1

        if "data_count" in params:
            page_size = int(params["data_count"])
            count = len(records)
            total_page_number = math.ceil(count / page_size)
        else:
            page_size = len(records)
            total_page_number = 1

        if "page" in params:
            current_page = int(params["page"])
        else:
            current_page = 1
        start = page_size*(current_page-1)
        stop = current_page*page_size
        records = records[start:stop]
        next_page = current_page+1 \
            if 0 < current_page + 1 <= total_page_number \
            else None
        prev_page = current_page-1 \
            if 0 < current_page - 1 <= total_page_number \
            else None

        try:
            serializer = Serializer(records, query, many=True)
            data = serializer.data
        except (SyntaxError, QueryFormatError) as e:
            res = error_response(e, e.msg)
            return self.make_json_response(res)
        res = {
            "count": len(records),
            "prev": prev_page,
            "current": current_page,
            "next": next_page,
            "total_pages": total_page_number,
            "operation_type": data
        }

        return self.make_json_response(res)

    @http.route('/api/stock-routes',type='http', auth='user',methods=['GET'])
    def get_model_stock_routes_data(self, **params):
        try:
            yesterday = datetime.datetime.now() - datetime.timedelta(days=1)
            yesterday_beginning = datetime.datetime(yesterday.year, yesterday.month, yesterday.day, 0, 0, 0, 0)
            yb = yesterday_beginning.strftime("%Y-%m-%d %I:%M:%S")
            today = datetime.datetime.now()
            today_beginning = datetime.datetime(today.year, today.month, today.day, 0, 0, 0, 0)
            tb = today_beginning.strftime("%Y-%m-%d %I:%M:%S")
            if "write_date" in params:
                tglawal ='%s %s' %(params['write_date'],'00:00:00')
                tglminta1 = datetime.datetime.strptime(tglawal, '%Y-%m-%d %H:%M:%S')
                tglakhir = '%s %s' %(params['write_date'],'23:59:59')
                tglminta2 = datetime.datetime.strptime(tglakhir, '%Y-%m-%d %H:%M:%S')
                records = request.env['stock.location.route'].search([('write_date','>=',tglminta1),('write_date','<',tglminta2)])
            elif "name" in params:
                records = request.env['stock.location.route'].search(
                    [('name','=', params['name'])])
            elif "company_id" in params:
                records = request.env['stock.location.route'].search(
                    [('company_id.name','=', params['company_id'])])
            elif "name" in params and "company_id" in params:
                records = request.env['stock.location.route'].search(
                    [('name','=',params['name']),('company_id.name','=', params['company_id'])])
            else:
                records = request.env['stock.location.route'].search(
                    [])
        except KeyError as e:
            msg = "The model `%s` does not exist." % 'product.product'
            return self.make_json_response(msg)
        query = "{*}"
        orders = ""
        prev_page = None
        next_page = None
        total_page_number = 1
        current_page = 1

        if "data_count" in params:
            page_size = int(params["data_count"])
            count = len(records)
            total_page_number = math.ceil(count / page_size)
        else:
            page_size = len(records)
            total_page_number = 1

        if "page" in params:
            current_page = int(params["page"])
        else:
            current_page = 1
        start = page_size*(current_page-1)
        stop = current_page*page_size
        records = records[start:stop]
        next_page = current_page+1 \
            if 0 < current_page + 1 <= total_page_number \
            else None
        prev_page = current_page-1 \
            if 0 < current_page - 1 <= total_page_number \
            else None

        try:
            serializer = Serializer(records, query, many=True)
            data = serializer.data
        except (SyntaxError, QueryFormatError) as e:
            res = error_response(e, e.msg)
            return self.make_json_response(res)
        res = {
            "count": len(records),
            "prev": prev_page,
            "current": current_page,
            "next": next_page,
            "total_pages": total_page_number,
            "stock_location_routes": data
        }

        return self.make_json_response(res)

    @http.route('/api/analiatic',type='http', auth='user',methods=['GET'])
    def get_model_analitic_data(self, **params):
        try:
            yesterday = datetime.datetime.now() - datetime.timedelta(days=1)
            yesterday_beginning = datetime.datetime(yesterday.year, yesterday.month, yesterday.day, 0, 0, 0, 0)
            yb = yesterday_beginning.strftime("%Y-%m-%d %I:%M:%S")
            today = datetime.datetime.now()
            today_beginning = datetime.datetime(today.year, today.month, today.day, 0, 0, 0, 0)
            tb = today_beginning.strftime("%Y-%m-%d %I:%M:%S")
            if "write_date" in params:
                tglawal ='%s %s' %(params['write_date'],'00:00:00')
                tglminta1 = datetime.datetime.strptime(tglawal, '%Y-%m-%d %H:%M:%S')
                tglakhir = '%s %s' %(params['write_date'],'23:59:59')
                tglminta2 = datetime.datetime.strptime(tglakhir, '%Y-%m-%d %H:%M:%S')
                records = request.env['product.product'].search([('write_date','>=',tglminta1),('write_date','<',tglminta2)])
            elif "name" in params:
                records = request.env['stock.rule'].search(
                    [('name','=', params['name'])])
            else:
                records = request.env['product.product'].search(
                    [])
        except KeyError as e:
            msg = "The model `%s` does not exist." % 'product.product'
            return self.make_json_response(msg)
        query = "{*}"
        orders = ""
        prev_page = None
        next_page = None
        total_page_number = 1
        current_page = 1

        if "data_count" in params:
            page_size = int(params["data_count"])
            count = len(records)
            total_page_number = math.ceil(count / page_size)
        else:
            page_size = len(records)
            total_page_number = 1

        if "page" in params:
            current_page = int(params["page"])
        else:
            current_page = 1
        start = page_size*(current_page-1)
        stop = current_page*page_size
        records = records[start:stop]
        next_page = current_page+1 \
            if 0 < current_page + 1 <= total_page_number \
            else None
        prev_page = current_page-1 \
            if 0 < current_page - 1 <= total_page_number \
            else None

        try:
            serializer = Serializer(records, query, many=True)
            data = serializer.data
        except (SyntaxError, QueryFormatError) as e:
            res = error_response(e, e.msg)
            return self.make_json_response(res)
        res = {
            "count": len(records),
            "prev": prev_page,
            "current": current_page,
            "next": next_page,
            "total_pages": total_page_number,
            "product_core": data
        }

        return self.make_json_response(res)

    @http.route('/api/stock-rules',type='http', auth='user',methods=['GET'])
    def get_model_stock_rulesdata(self, **params):
        try:
            yesterday = datetime.datetime.now() - datetime.timedelta(days=1)
            yesterday_beginning = datetime.datetime(yesterday.year, yesterday.month, yesterday.day, 0, 0, 0, 0)
            yb = yesterday_beginning.strftime("%Y-%m-%d %I:%M:%S")
            today = datetime.datetime.now()
            today_beginning = datetime.datetime(today.year, today.month, today.day, 0, 0, 0, 0)
            tb = today_beginning.strftime("%Y-%m-%d %I:%M:%S")
            if "write_date" in params:
                tglawal ='%s %s' %(params['write_date'],'00:00:00')
                tglminta1 = datetime.datetime.strptime(tglawal, '%Y-%m-%d %H:%M:%S')
                tglakhir = '%s %s' %(params['write_date'],'23:59:59')
                tglminta2 = datetime.datetime.strptime(tglakhir, '%Y-%m-%d %H:%M:%S')
                records = request.env['stock.rule'].search([('write_date','>=',tglminta1),('write_date','<',tglminta2)])
            elif "name" in params:
                records = request.env['stock.rule'].search(
                    [('name','=', params['name'])])
            elif "route_id" in params and "company_id" in params:
                records = request.env['stock.rule'].search(
                    [('route_id.name','=', params['route_id']),('company_id.name','=',params['company_id'])])
            elif "company_id" in params:
                records = request.env['stock.rule'].search(
                    [('company_id.name','=', params['company_id'])])
            else:
                records = request.env['stock.rule'].search(
                    [])
        except KeyError as e:
            msg = "The model `%s` does not exist." % 'stock.rule'
            return self.makresponse(msg)
        query = "{*}"
        orders = ""
        prev_page = None
        next_page = None
        total_page_number = 1
        current_page = 1

        if "data_count" in params:
            page_size = int(params["data_count"])
            count = len(records)
            total_page_number = math.ceil(count / page_size)
        else:
            page_size = len(records)
            total_page_number = 1

        if "page" in params:
            current_page = int(params["page"])
        else:
            current_page = 1
        start = page_size*(current_page-1)
        stop = current_page*page_size
        records = records[start:stop]
        next_page = current_page+1 \
            if 0 < current_page + 1 <= total_page_number \
            else None
        prev_page = current_page-1 \
            if 0 < current_page - 1 <= total_page_number \
            else None

        try:
            serializer = Serializer(records, query, many=True)
            data = serializer.data
        except (SyntaxError, QueryFormatError) as e:
            res = error_response(e, e.msg)
            return self.make_json_response(res)
        res = {
            "count": len(records),
            "prev": prev_page,
            "current": current_page,
            "next": next_page,
            "total_pages": total_page_number,
            "stock_rules": data
        }

        return self.make_json_response(res)


    @http.route('/api/stock-putaway-rules',type='http', auth='user',methods=['GET'])
    def get_model_stock_putaway_rules_data(self, **params):
        try:
            yesterday = datetime.datetime.now() - datetime.timedelta(days=1)
            yesterday_beginning = datetime.datetime(yesterday.year, yesterday.month, yesterday.day, 0, 0, 0, 0)
            yb = yesterday_beginning.strftime("%Y-%m-%d %I:%M:%S")
            today = datetime.datetime.now()
            today_beginning = datetime.datetime(today.year, today.month, today.day, 0, 0, 0, 0)
            tb = today_beginning.strftime("%Y-%m-%d %I:%M:%S")
            if "write_date" in params:
                tglawal ='%s %s' %(params['write_date'],'00:00:00')
                tglminta1 = datetime.datetime.strptime(tglawal, '%Y-%m-%d %H:%M:%S')
                tglakhir = '%s %s' %(params['write_date'],'23:59:59')
                tglminta2 = datetime.datetime.strptime(tglakhir, '%Y-%m-%d %H:%M:%S')
                records = request.env['stock.putaway.rule'].search([('write_date','>=',tglminta1),('write_date','<',tglminta2)])
            elif "name" in params:
                records = request.env['stock.putaway.rule'].search(
                    [('name','=', params['name'])])
            elif "company_id" in params:
                records = request.env['stock.putaway.rule'].search(
                    [('company_id.name','=', params['company_id'])])
            else:
                records = request.env['stock.putaway.rule'].search(
                    [])
        except KeyError as e:
            msg = "The model `%s` does not exist." % 'stock.putaway.rule'
            return self.make_json_response(msg)
        query = "{*}"
        orders = ""
        prev_page = None
        next_page = None
        total_page_number = 1
        current_page = 1

        if "data_count" in params:
            page_size = int(params["data_count"])
            count = len(records)
            total_page_number = math.ceil(count / page_size)
        else:
            page_size = len(records)
            total_page_number = 1

        if "page" in params:
            current_page = int(params["page"])
        else:
            current_page = 1
        start = page_size*(current_page-1)
        stop = current_page*page_size
        records = records[start:stop]
        next_page = current_page+1 \
            if 0 < current_page + 1 <= total_page_number \
            else None
        prev_page = current_page-1 \
            if 0 < current_page - 1 <= total_page_number \
            else None

        try:
            serializer = Serializer(records, query, many=True)
            data = serializer.data
        except (SyntaxError, QueryFormatError) as e:
            res = error_response(e, e.msg)
            return self.make_json_response(res)
        res = {
            "count": len(records),
            "prev": prev_page,
            "current": current_page,
            "next": next_page,
            "total_pages": total_page_number,
            "putaway_rules": data
        }

        return self.make_json_response(res)


    @http.route('/api/product-uom', type='http', auth='user', methods=['GET'])
    def get_model_product_uom_data(self, **params):
        try:
            yesterday = datetime.datetime.now() - datetime.timedelta(days=1)
            yesterday_beginning = datetime.datetime(yesterday.year, yesterday.month, yesterday.day, 0, 0, 0, 0)
            yb = yesterday_beginning.strftime("%Y-%m-%d %I:%M:%S")
            today = datetime.datetime.now()
            today_beginning = datetime.datetime(today.year, today.month, today.day, 0, 0, 0, 0)
            tb = today_beginning.strftime("%Y-%m-%d %I:%M:%S")
            if "write_date" in params:
                tglawal = '%s %s' % (params['write_date'], '00:00:00')
                tglminta1 = datetime.datetime.strptime(tglawal, '%Y-%m-%d %H:%M:%S')
                tglakhir = '%s %s' % (params['write_date'], '23:59:59')
                tglminta2 = datetime.datetime.strptime(tglakhir, '%Y-%m-%d %H:%M:%S')
                records = request.env['uom.uom'].search(
                    [('write_date', '>=', tglminta1), ('write_date', '<', tglminta2)])
            elif "name" in params:
                records = request.env['uom.uom'].search(
                    [('name','=', params['name'])])
            else:
                records = request.env['uom.uom'].search(
                    [])
        except KeyError as e:
            msg = "The model `%s` does not exist." % 'uom.uom'
            return self.make_json_response(msg)
        query = "{*}"
        orders = ""
        prev_page = None
        next_page = None
        total_page_number = 1
        current_page = 1

        if "data_count" in params:
            page_size = int(params["data_count"])
            count = len(records)
            total_page_number = math.ceil(count / page_size)
        else:
            page_size = len(records)
            total_page_number = 1

        if "page" in params:
            current_page = int(params["page"])
        else:
            current_page = 1
        start = page_size * (current_page - 1)
        stop = current_page * page_size
        records = records[start:stop]
        next_page = current_page + 1 \
            if 0 < current_page + 1 <= total_page_number \
            else None
        prev_page = current_page - 1 \
            if 0 < current_page - 1 <= total_page_number \
            else None

        try:
            serializer = Serializer(records, query, many=True)
            data = serializer.data
        except (SyntaxError, QueryFormatError) as e:
            res = error_response(e, e.msg)
            return self.make_json_response(res)
        res = {
            "count": len(records),
            "prev": prev_page,
            "current": current_page,
            "next": next_page,
            "total_pages": total_page_number,
            "stock_uom": data
        }

        return self.make_json_response(res)

    @http.route('/api/product-uom-category', type='http', auth='user', methods=['GET'])
    def get_model_product_uom_categ_data(self, **params):
        try:
            yesterday = datetime.datetime.now() - datetime.timedelta(days=1)
            yesterday_beginning = datetime.datetime(yesterday.year, yesterday.month, yesterday.day, 0, 0, 0, 0)
            yb = yesterday_beginning.strftime("%Y-%m-%d %I:%M:%S")
            today = datetime.datetime.now()
            today_beginning = datetime.datetime(today.year, today.month, today.day, 0, 0, 0, 0)
            tb = today_beginning.strftime("%Y-%m-%d %I:%M:%S")
            if "write_date" in params:
                tglawal = '%s %s' % (params['write_date'], '00:00:00')
                tglminta1 = datetime.datetime.strptime(tglawal, '%Y-%m-%d %H:%M:%S')
                tglakhir = '%s %s' % (params['write_date'], '23:59:59')
                tglminta2 = datetime.datetime.strptime(tglakhir, '%Y-%m-%d %H:%M:%S')
                records = request.env['uom.category'].search(
                    [('write_date', '>=', tglminta1), ('write_date', '<', tglminta2)])
            elif "name" in params:

                records = request.env['uom.category'].search(
                    [('name','=', params['name'])])
                print('nama category', records)
            else:
                records = request.env['uom.category'].search(
                    [])
        except KeyError as e:
            msg = "The model `%s` does not exist." % 'uom.uom'
            return self.make_json_response(msg)
        query = "{*}"
        orders = ""
        prev_page = None
        next_page = None
        total_page_number = 1
        current_page = 1

        if "data_count" in params:
            page_size = int(params["data_count"])
            count = len(records)
            total_page_number = math.ceil(count / page_size)
        else:
            page_size = len(records)
            total_page_number = 1

        if "page" in params:
            current_page = int(params["page"])
        else:
            current_page = 1
        start = page_size * (current_page - 1)
        stop = current_page * page_size
        records = records[start:stop]
        next_page = current_page + 1 \
            if 0 < current_page + 1 <= total_page_number \
            else None
        prev_page = current_page - 1 \
            if 0 < current_page - 1 <= total_page_number \
            else None

        try:
            serializer = Serializer(records, query, many=True)
            data = serializer.data
        except (SyntaxError, QueryFormatError) as e:
            res = error_response(e, e.msg)
            return self.make_json_response(res)
        res = {
            "count": len(records),
            "prev": prev_page,
            "current": current_page,
            "next": next_page,
            "total_pages": total_page_number,
            "stock_uom_categ": data
        }

        return self.make_json_response(res)

    @http.route('/api/coa', type='http', auth='user', methods=['GET'])
    def get_model_coa_data(self, **params):
        try:
            yesterday = datetime.datetime.now() - datetime.timedelta(days=1)
            yesterday_beginning = datetime.datetime(yesterday.year, yesterday.month, yesterday.day, 0, 0, 0, 0)
            yb = yesterday_beginning.strftime("%Y-%m-%d %I:%M:%S")
            today = datetime.datetime.now()
            today_beginning = datetime.datetime(today.year, today.month, today.day, 0, 0, 0, 0)
            tb = today_beginning.strftime("%Y-%m-%d %I:%M:%S")
            if "write_date" in params:
                tglawal = '%s %s' % (params['write_date'], '00:00:00')
                tglminta1 = datetime.datetime.strptime(tglawal, '%Y-%m-%d %H:%M:%S')
                tglakhir = '%s %s' % (params['write_date'], '23:59:59')
                tglminta2 = datetime.datetime.strptime(tglakhir, '%Y-%m-%d %H:%M:%S')
                records = request.env['account.account'].search(
                    [('write_date', '>=', tglminta1), ('write_date', '<', tglminta2)])
            elif "name" in params:
                records = request.env['account.account'].search(
                    [('name','=', params['name'])])
            else:
                records = request.env['account.account'].search(
                    [])
        except KeyError as e:
            msg = "The model `%s` does not exist." % 'uom.uom'
            return self.make_json_response(msg)
        query = "{*}"
        orders = ""
        prev_page = None
        next_page = None
        total_page_number = 1
        current_page = 1

        if "data_count" in params:
            page_size = int(params["data_count"])
            count = len(records)
            total_page_number = math.ceil(count / page_size)
        else:
            page_size = len(records)
            total_page_number = 1

        if "page" in params:
            current_page = int(params["page"])
        else:
            current_page = 1
        start = page_size * (current_page - 1)
        stop = current_page * page_size
        records = records[start:stop]
        next_page = current_page + 1 \
            if 0 < current_page + 1 <= total_page_number \
            else None
        prev_page = current_page - 1 \
            if 0 < current_page - 1 <= total_page_number \
            else None

        try:
            serializer = Serializer(records, query, many=True)
            data = serializer.data
        except (SyntaxError, QueryFormatError) as e:
            res = error_response(e, e.msg)
            return self.make_json_response(res)
        res = {
            "count": len(records),
            "prev": prev_page,
            "current": current_page,
            "next": next_page,
            "total_pages": total_page_number,
            "coa_core": data
        }

        return self.make_json_response(res)

    @http.route('/api/account-account-type', type='http', auth='user', methods=['GET'])
    def get_model_account_account_type_data(self, **params):
        try:
            yesterday = datetime.datetime.now() - datetime.timedelta(days=1)
            yesterday_beginning = datetime.datetime(yesterday.year, yesterday.month, yesterday.day, 0, 0, 0, 0)
            yb = yesterday_beginning.strftime("%Y-%m-%d %I:%M:%S")
            today = datetime.datetime.now()
            today_beginning = datetime.datetime(today.year, today.month, today.day, 0, 0, 0, 0)
            tb = today_beginning.strftime("%Y-%m-%d %I:%M:%S")
            if "write_date" in params:
                tglawal = '%s %s' % (params['write_date'], '00:00:00')
                tglminta1 = datetime.datetime.strptime(tglawal, '%Y-%m-%d %H:%M:%S')
                tglakhir = '%s %s' % (params['write_date'], '23:59:59')
                tglminta2 = datetime.datetime.strptime(tglakhir, '%Y-%m-%d %H:%M:%S')
                records = request.env['account.account.type'].search(
                    [('write_date', '>=', tglminta1), ('write_date', '<', tglminta2)])
            elif "name" in params:
                records = request.env['account.account.type'].search(
                    [('name','=', params['name'])])
            else:
                records = request.env['account.account.type'].search(
                    [])
        except KeyError as e:
            msg = "The model `%s` does not exist." % 'uom.uom'
            return self.make_json_response(msg)
        query = "{*}"
        orders = ""
        prev_page = None
        next_page = None
        total_page_number = 1
        current_page = 1

        if "data_count" in params:
            page_size = int(params["data_count"])
            count = len(records)
            total_page_number = math.ceil(count / page_size)
        else:
            page_size = len(records)
            total_page_number = 1

        if "page" in params:
            current_page = int(params["page"])
        else:
            current_page = 1
        start = page_size * (current_page - 1)
        stop = current_page * page_size
        records = records[start:stop]
        next_page = current_page + 1 \
            if 0 < current_page + 1 <= total_page_number \
            else None
        prev_page = current_page - 1 \
            if 0 < current_page - 1 <= total_page_number \
            else None

        try:
            serializer = Serializer(records, query, many=True)
            data = serializer.data
        except (SyntaxError, QueryFormatError) as e:
            res = error_response(e, e.msg)
            return self.make_json_response(res)
        res = {
            "count": len(records),
            "prev": prev_page,
            "current": current_page,
            "next": next_page,
            "total_pages": total_page_number,
            "account_account_type": data
        }

        return self.make_json_response(res)

    @http.route('/api/account-group', type='http', auth='user', methods=['GET'])
    def get_model_account_group_data(self, **params):
        try:
            yesterday = datetime.datetime.now() - datetime.timedelta(days=1)
            yesterday_beginning = datetime.datetime(yesterday.year, yesterday.month, yesterday.day, 0, 0, 0, 0)
            yb = yesterday_beginning.strftime("%Y-%m-%d %I:%M:%S")
            today = datetime.datetime.now()
            today_beginning = datetime.datetime(today.year, today.month, today.day, 0, 0, 0, 0)
            tb = today_beginning.strftime("%Y-%m-%d %I:%M:%S")
            if "write_date" in params:
                tglawal = '%s %s' % (params['write_date'], '00:00:00')
                tglminta1 = datetime.datetime.strptime(tglawal, '%Y-%m-%d %H:%M:%S')
                tglakhir = '%s %s' % (params['write_date'], '23:59:59')
                tglminta2 = datetime.datetime.strptime(tglakhir, '%Y-%m-%d %H:%M:%S')
                records = request.env['account.group'].search(
                    [('write_date', '>=', tglminta1), ('write_date', '<', tglminta2)])
            elif "name" in params:
                records = request.env['account.group'].search(
                    [('name','=', params['name'])])
            else:
                records = request.env['account.group'].search(
                    [])
        except KeyError as e:
            msg = "The model `%s` does not exist." % 'uom.uom'
            return self.make_json_response(msg)
        query = "{*}"
        orders = ""
        prev_page = None
        next_page = None
        total_page_number = 1
        current_page = 1

        if "data_count" in params:
            page_size = int(params["data_count"])
            count = len(records)
            total_page_number = math.ceil(count / page_size)
        else:
            page_size = len(records)
            total_page_number = 1

        if "page" in params:
            current_page = int(params["page"])
        else:
            current_page = 1
        start = page_size * (current_page - 1)
        stop = current_page * page_size
        records = records[start:stop]
        next_page = current_page + 1 \
            if 0 < current_page + 1 <= total_page_number \
            else None
        prev_page = current_page - 1 \
            if 0 < current_page - 1 <= total_page_number \
            else None

        try:
            serializer = Serializer(records, query, many=True)
            data = serializer.data
        except (SyntaxError, QueryFormatError) as e:
            res = error_response(e, e.msg)
            return self.make_json_response(res)
        res = {
            "count": len(records),
            "prev": prev_page,
            "current": current_page,
            "next": next_page,
            "total_pages": total_page_number,
            "account_group": data
        }

        return self.make_json_response(res)

    @http.route('/api/analityc-default', type='http', auth='user', methods=['GET'])
    def get_model_account_group_data(self, **params):
        try:
            yesterday = datetime.datetime.now() - datetime.timedelta(days=1)
            yesterday_beginning = datetime.datetime(yesterday.year, yesterday.month, yesterday.day, 0, 0, 0, 0)
            yb = yesterday_beginning.strftime("%Y-%m-%d %I:%M:%S")
            today = datetime.datetime.now()
            today_beginning = datetime.datetime(today.year, today.month, today.day, 0, 0, 0, 0)
            tb = today_beginning.strftime("%Y-%m-%d %I:%M:%S")
            if "write_date" in params:
                tglawal = '%s %s' % (params['write_date'], '00:00:00')
                tglminta1 = datetime.datetime.strptime(tglawal, '%Y-%m-%d %H:%M:%S')
                tglakhir = '%s %s' % (params['write_date'], '23:59:59')
                tglminta2 = datetime.datetime.strptime(tglakhir, '%Y-%m-%d %H:%M:%S')
                records = request.env['account.analytic.default'].search(
                    [('write_date', '>=', tglminta1), ('write_date', '<', tglminta2)])
            elif "name" in params:
                records = request.env['account.analytic.default'].search(
                    [('name','=', params['name'])])
            else:
                records = request.env['account.analytic.default'].search(
                    [])
        except KeyError as e:
            msg = "The model `%s` does not exist." % 'uom.uom'
            return self.make_json_response(msg)
        query = "{*}"
        orders = ""
        prev_page = None
        next_page = None
        total_page_number = 1
        current_page = 1

        if "data_count" in params:
            page_size = int(params["data_count"])
            count = len(records)
            total_page_number = math.ceil(count / page_size)
        else:
            page_size = len(records)
            total_page_number = 1

        if "page" in params:
            current_page = int(params["page"])
        else:
            current_page = 1
        start = page_size * (current_page - 1)
        stop = current_page * page_size
        records = records[start:stop]
        next_page = current_page + 1 \
            if 0 < current_page + 1 <= total_page_number \
            else None
        prev_page = current_page - 1 \
            if 0 < current_page - 1 <= total_page_number \
            else None

        try:
            serializer = Serializer(records, query, many=True)
            data = serializer.data
        except (SyntaxError, QueryFormatError) as e:
            res = error_response(e, e.msg)
            return self.make_json_response(res)
        res = {
            "count": len(records),
            "prev": prev_page,
            "current": current_page,
            "next": next_page,
            "total_pages": total_page_number,
            "account_group": data
        }

        return self.make_json_response(res)