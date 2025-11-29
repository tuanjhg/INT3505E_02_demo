"""
Developer Portal Routes
-----------------------
Blueprint để serve các trang Developer Portal (API as Product)
"""

from flask import Blueprint, render_template

# Tạo Blueprint cho Developer Portal
portal_bp = Blueprint('portal', __name__, 
                      url_prefix='/portal',
                      template_folder='../templates/developer_portal')


@portal_bp.route('/')
def index():
    """
    Trang chủ Developer Portal
    """
    return render_template('developer_portal/index.html')


@portal_bp.route('/docs')
def docs():
    """
    Trang API Documentation
    """
    return render_template('developer_portal/docs.html')


@portal_bp.route('/explorer')
def explorer():
    """
    Trang API Explorer - thử nghiệm API trực tiếp
    """
    return render_template('developer_portal/explorer.html')


@portal_bp.route('/getting-started')
def getting_started():
    """
    Trang Getting Started - hướng dẫn bắt đầu nhanh
    """
    return render_template('developer_portal/getting_started.html')
