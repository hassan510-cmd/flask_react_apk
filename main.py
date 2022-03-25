import sqlalchemy
from sqlalchemy.sql import func
from flask import Flask, request
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from werkzeug.utils import secure_filename
from marshmallow import fields

UPLOAD_FOLDER = '/htmls/assets/'
ALLOWED_EXTENSIONS = { 'png', 'jpg', 'jpeg'}
app = Flask(__name__,
            static_folder='./htmls/',
            static_url_path="/htmls/"  # http://127.0.0.1/ui/
            )
CORS(app)
# api = Api(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.config['MAX_CONTENT_LENGTH'] = 10 * 1000
# 10 * 1000 = 10kb
# 10 * 1000 * 1000 = 10mb
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
# init db
db = SQLAlchemy(app)

# init ma
ma = Marshmallow(app)



# ========================================================================
# ======================= models =========================================
class UserModel(db.Model):
    user_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255))
    password = db.Column(db.String(255), default="p@s$wo0rd")
    email = db.Column(db.String(255))

    def __init__(self, username, password, email):
        self.username = username
        self.password = password
        self.email = email

    def __str__(self):
        return self.username

class TimeSheetModel(db.Model):
    __tablename__="TimeSheetModel"
    __table_args__=(
        db.UniqueConstraint("sheet_year", "sheet_month", name="unique_month_year"),
    )
    sheet_id = db.Column(db.Integer, primary_key=True)
    sheet_name = db.Column(db.String(225))
    sheet_year = db.Column(db.Integer)
    sheet_month = db.Column(db.Integer)
    total_income = db.Column(db.Float, default=0.0)
    total_spent = db.Column(db.Float, default=0.0)
    total_remain = db.Column(db.Float, default=0.0)
    purchase_order_ids = db.relationship("PurchaseOrderModel")

    def __str__(self):
        return self.sheet_name

    def __init__(self, sheet_name, sheet_year, sheet_month,total_income,total_remain):
        self.sheet_name = sheet_name
        self.sheet_year = sheet_year
        self.sheet_month = sheet_month
        self.total_income = total_income
        self.total_remain = total_remain

class CategoryModel(db.Model):
    __tablename__="CategoryModel"
    category_id = db.Column(db.Integer, primary_key=True)
    category_name = db.Column(db.String(225))
    category_image = db.Column(db.String(3000))


    def __str__(self):
        return self.category_name

    def __init__(self, category_name,category_image):
        self.category_name = category_name
        self.category_image = category_image

class PurchaseOrderModel(db.Model):
    PO_id = db.Column(db.Integer, primary_key=True)
    rel_category = db.Column(db.Integer)
    timesheet_id = db.Column(db.Integer,db.ForeignKey("TimeSheetModel.sheet_id"))
    product_name = db.Column(db.String(225))
    price = db.Column(db.Float, default=0.0)
    is_payed = db.Column(db.Boolean, default=False)
    write_date = db.Column(db.DateTime(timezone=True), server_default=func.now())

    def __init__(self, rel_category,timesheet_id, product_name, price):
        self.timesheet_id = timesheet_id
        self.rel_category = rel_category
        self.product_name = product_name
        self.price = price

class IncomeSourceModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(225),unique=True)
    total = db.Column(db.Float, default=0.0,nullable=True)

    def __init__(self, name,total):
        self.total = total
        self.name = name

# ========================================================================
# ======================= serializer =====================================
class UserSerializer(ma.Schema):
    class Meta:
        fields = ("username", "user_id", "email")

class TimeSheetSerializer(ma.Schema):
    class Meta:
        fields = ("sheet_id", "sheet_name",
                  "sheet_year", "sheet_month",
                  "total_income", "total_spent", "total_remain")

class PurchaseOrderSerializer(ma.Schema):
    class Meta:
        fields = ("PO_id", "rel_category", "timesheet_id", "product_name", "price", "is_payed", "write_date")

class CategorySerializer(ma.Schema):
    order_counter = fields.Method("get_all_related_orders_number")
    payed_orders = fields.Method("get_all_payed_orders_number")
    def get_all_related_orders_number(self,obj):
        timesheet_id = request.args.get("timesheet_id")
        if timesheet_id :
            return PurchaseOrderModel.query.filter_by(rel_category=obj.category_id,timesheet_id=timesheet_id).count()
        return PurchaseOrderModel.query.filter_by(rel_category=obj.category_id).count()
    def get_all_payed_orders_number(self,obj):
        timesheet_id = request.args.get("timesheet_id")
        if timesheet_id :
            return PurchaseOrderModel.query.filter_by(is_payed=True,rel_category=obj.category_id,timesheet_id=timesheet_id).count()
        return PurchaseOrderModel.query.filter_by(rel_category=obj.category_id).count()
    class Meta:
        fields = ("category_id", "category_name","category_image","order_counter","payed_orders")
class IncomeSourceSerializer(ma.Schema):
    class Meta:
        fields = ("id", "name", "total")

# ================================================================
# ==================== application routes ========================

@app.route("/user", methods=['POST'])
def add_user():
    if request.is_json:
        username = request.json.get("username")
        password = request.json.get("password")
        email = request.json.get("email")
    new_user = UserModel(username=username, password=password, email=email)
    db.session.add(new_user)
    db.session.commit()
    return UserSerializer().jsonify(new_user)

@app.route("/timesheet", methods=['POST'])
def add_timesheet():
    if request.is_json:
        sheet_name = request.json.get("sheet_name")
        sheet_year = request.json.get("sheet_year")
        sheet_month = request.json.get("sheet_month")
        total_income = request.json.get("total_income")
        total_remain = request.json.get("total_remain")
    new_timesheet = TimeSheetModel(sheet_name=sheet_name, sheet_year=sheet_year,
                                   sheet_month=sheet_month,
                                   total_remain=total_remain,
                                   total_income=total_income)
    db.session.add(new_timesheet)
    db.session.commit()
    return TimeSheetSerializer().jsonify(new_timesheet)

@app.route("/category", methods=['GET','POST'])
def add_category():
    image_path =""
    if len(request.files.getlist("category_image"))>0:
        file = request.files.getlist("category_image")[0]
        filename = secure_filename(file.filename)
        image_path = f"{UPLOAD_FOLDER}{filename}"
        file.save(f"./{image_path}")
    if request.is_json:
        category_name = request.json.get("category_name")
    else:
        category_name = request.form.get("category_name")
    new_category = CategoryModel(category_name=category_name,category_image=image_path)
    db.session.add(new_category)
    db.session.commit()
    return CategorySerializer().jsonify(new_category)

@app.route("/purchase-order", methods=['POST'])
def add_purchase_order():
    if request.is_json:
        rel_category = request.json.get("rel_category")
        product_name = request.json.get("product_name")
        price = request.json.get("price")
        timesheet_id = request.json.get("timesheet_id")
    new_purchase_order = PurchaseOrderModel(rel_category=rel_category, product_name=product_name,price=price,timesheet_id=timesheet_id )
    db.session.add(new_purchase_order)
    db.session.commit()
    return PurchaseOrderSerializer().jsonify(new_purchase_order)

@app.route("/income-source", methods=['POST'])
def add_income_source():
    if request.is_json:
        source_name = request.json.get("name")
        total = request.json.get("total")
        new_order_source = IncomeSourceModel(name=source_name, total=total)
        db.session.add(new_order_source)
        db.session.commit()
        return IncomeSourceSerializer().jsonify(new_order_source)
    return "invalid data"

@app.route('/get_timesheet')
def get_single_timesheet():
    timesheet_id = request.args.get("timesheet_id")
    result  = TimeSheetModel.query.get(timesheet_id)
    return TimeSheetSerializer().jsonify(result)

# ================================ Getters [all] ========================================
@app.route("/users", methods=['GET'])
def get_all_users():
    users = UserModel.query.all()
    return UserSerializer(many=True).jsonify(many=True, obj=users)

@app.route("/all_timesheet", methods=['GET'])
def get_all_timesheet():
    result = TimeSheetModel.query.all()
    return TimeSheetSerializer(many=True).jsonify(many=True, obj=result)

@app.route("/categories", methods=['GET'])
def get_all_categories():
    result = CategoryModel.query.all()
    return CategorySerializer(many=True).jsonify(many=True, obj=result)

@app.route("/purchase-orders", methods=['GET'])
def get_all_purchase_orders():
    result = PurchaseOrderModel.query.all()
    return PurchaseOrderSerializer(many=True).jsonify(many=True, obj=result)

@app.route("/update-purchase-order-state", methods=['POST'])
def update_purchase_order_state():
    print("="*80)
    if request.is_json:
        print(request.json)
        order_id = request.json.get("order_id")
        order_state = request.json.get("order_state")
        order = PurchaseOrderModel.query.get(order_id)
        print(order)
        order.is_payed = order_state
        db.session.commit()
    return PurchaseOrderSerializer().jsonify(obj=order)

@app.route("/balance-timesheet", methods=['POST'])
def balance_timesheet():
    if request.is_json:
        timesheet_id = request.json.get("timesheet_id")
        total_spent = request.json.get("total_spent")
        timesheet = TimeSheetModel.query.filter_by(sheet_id=timesheet_id).first()
        print(total_spent)
        timesheet.total_spent += total_spent
        timesheet.total_remain = timesheet.total_income - timesheet.total_spent
        db.session.commit()
    return TimeSheetSerializer().jsonify(obj=timesheet)

@app.route("/income-sources", methods=['GET'])
def get_all_income_sources():
    result = IncomeSourceModel.query.all()
    return IncomeSourceSerializer(many=True).jsonify(many=True, obj=result)


@app.route('/po_by_category_timesheet')
def get_po_by_category_timesheet():
    print(request.args.get("category_id"))
    category_id = request.args.get("category_id")
    timesheet_id = request.args.get("timesheet_id")
    result = PurchaseOrderModel.query.filter_by(rel_category=category_id,timesheet_id=timesheet_id)
    return PurchaseOrderSerializer(many=True).jsonify(many=True,obj=result)

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def catch_all(path):
    return app.send_static_file("index.html")


@app.route("/get")
def show():
    return {"data": [1, 2, 3]}


if __name__ == "__main__":
    db.create_all()
    print("http://127.0.0.1:8888/ui/")
    app.run(host="0.0.0.0", port=8888, debug=False)
