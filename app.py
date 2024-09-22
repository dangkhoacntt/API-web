from flask import Flask
from controllers.auth_controller import auth_bp
from controllers.user_controller import user_bp
from controllers.main_controller import main_bp
from controllers.admin_controller import admin_bp
from controllers.user_list_controller import user_list_bp
from db import get_db_connection, close_db_connection
from config import Config
from mail_config import mail

app = Flask(__name__, template_folder='views')
app.config.from_object(Config)

# Khởi tạo mail
mail.init_app(app)

# Đăng ký blueprint
app.register_blueprint(auth_bp)
app.register_blueprint(user_bp)
app.register_blueprint(main_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(user_list_bp)

# Mở kết nối cơ sở dữ liệu trước mỗi yêu cầu
@app.before_request
def before_request():
    get_db_connection()

# Đóng kết nối DB sau khi request kết thúc
@app.teardown_appcontext
def teardown_appcontext(exception=None):
    close_db_connection()

if __name__ == '__main__':
    app.run(debug=True)
