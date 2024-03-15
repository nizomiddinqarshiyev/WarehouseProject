
from sqlalchemy import (
    Column, ForeignKey, Integer, String,
    Text, TIMESTAMP, DECIMAL, UniqueConstraint,
    MetaData, Boolean, Float, Date, event, Enum
)
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()
metadata = MetaData()


class Product(Base):
    __tablename__ = 'product'
    metadata = metadata
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column('name', String)
    description = Column('description', String)
    category_id = Column('category', Integer, ForeignKey('category.id'))
    unit_id = Column('unit', Integer, ForeignKey('unit.id'))
    price = Column('price', Float)
    last_updated = Column('last_updated', TIMESTAMP(), default=datetime.utcnow())

    unit = relationship('Unit', back_populates='product')
    category = relationship('Category', back_populates='product')
    order = relationship('Order', back_populates='product')
    history = relationship('ProductHistory', back_populates='product')
    product_location = relationship('ProductLocation', back_populates='product')
    composite = relationship('Composite', back_populates='product')
    recipe = relationship('Recipe', back_populates='product')


class Unit(Base):
    __tablename__ = 'unit'
    metadata = metadata
    id = Column(Integer, primary_key=True, autoincrement=True)
    code = Column('code', String, unique=True)
    name = Column('name', String)

    product = relationship('Product', back_populates='unit')
    resource = relationship('Resource', back_populates='unit')


class Shift(Base):
    __tablename__ = 'shift'
    metadata = metadata
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String)

    user = relationship('User', back_populates='shift')


class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True, autoincrement=True)
    metadata = metadata
    firstname = Column('firstname', String)
    lastname = Column('lastname', String)
    login = Column('login', String, unique=True)
    email = Column('email', String, unique=True)
    phone = Column('phone', String)
    password = Column('password', String)
    warehouse_id = Column(Integer, ForeignKey('warehouse.id', ondelete='CASCADE'))
    shift_id = Column(Integer, ForeignKey('shift.id', ondelete='CASCADE'))
    last_updated = Column('last_updated', TIMESTAMP(), default=datetime.utcnow())
    image = Column('image', String, nullable=True)

    shift = relationship('Shift', back_populates='user')
    warehouse = relationship('Warehouse', back_populates='user')
    composite = relationship('Composite', back_populates='employee')
    order_detail = relationship('OrderDetail', back_populates='user')
    user_role = relationship('UserRoles', back_populates='user')


class Role(Base):
    __tablename__ = 'role'
    id = Column(Integer, primary_key=True, autoincrement=True)
    metadata = metadata
    name = Column('name', String)
    description = Column('description', String)

    user_role = relationship('UserRoles', back_populates='role')


class UserRoles(Base):
    __tablename__ = 'user_role'
    id = Column(Integer, primary_key=True, autoincrement=True)
    metadata = metadata
    user_id = Column('user_id', Integer, ForeignKey('user.id'))
    role_id = Column('role_id', Integer, ForeignKey('role.id'))

    user = relationship('User', back_populates='user_role')
    role = relationship('Role', back_populates='user_role')


class Category(Base):
    __tablename__ = 'category'
    id = Column(Integer, primary_key=True, autoincrement=True)
    metadata = metadata
    name = Column('name', String)
    description = Column('description', String)

    product = relationship('Product', back_populates='category')
    warehouse_type = relationship('WarehouseType', back_populates='category')


class OrderDetail(Base):
    __tablename__ = 'order_detail'
    id = Column(Integer, primary_key=True, autoincrement=True)
    metadata = metadata
    costumer_id = Column('costumer', Integer, ForeignKey('costumer.id'))
    paid = Column('paid', Float)
    total_price = Column('total_price', Float)
    user_id = Column('user_id', Integer, ForeignKey('user.id'))
    created_at = Column('created_at', TIMESTAMP(), default=datetime.utcnow())
    is_active = Column('is_active', Boolean, default=True)

    costumer = relationship('Costumer', foreign_keys=[costumer_id], back_populates='order_detail')
    user = relationship('User', back_populates='order_detail')
    order = relationship('Order', back_populates='order_detail')


class Order(Base):
    __tablename__ = 'order'
    id = Column(Integer, primary_key=True, autoincrement=True)
    metadata = metadata
    product_id = Column('product_id', Integer, ForeignKey('product.id'))
    warehouse_id = Column('warehouse_id', Integer, ForeignKey('warehouse.id'))
    order_detail_id = Column('order_detail_id', Integer, ForeignKey('order_detail.id'))
    count = Column('count', Integer)

    order_detail = relationship('OrderDetail', back_populates='order')
    warehouse = relationship('Warehouse', back_populates='order')
    product = relationship('Product', back_populates='order')


class Costumer(Base):
    __tablename__ = 'costumer'
    metadata = metadata
    id = Column(Integer, primary_key=True, autoincrement=True)
    firstname = Column('firstname', String)
    lastname = Column('lastname', String)
    phone = Column('phone', String, unique=True)
    email = Column('email', String, unique=True)
    created_at = Column('created_at', TIMESTAMP(), default=datetime.utcnow())
    last_login = Column('last_login', TIMESTAMP())
    user_id = Column('user_id', Integer, ForeignKey('user.id'))

    order_detail = relationship('OrderDetail', back_populates='costumer')


class ProductHistory(Base):
    __tablename__ = 'product_history'
    metadata = metadata
    id = Column('id', Integer, primary_key=True, autoincrement=True)
    product_id = Column('product_id', Integer, ForeignKey('product.id'))
    warehouse_old_id = Column('warehouse_old_id', Integer, ForeignKey('warehouse.id'))
    warehouse_new_id = Column('warehouse_new_id', Integer, ForeignKey('warehouse.id'))
    last_update = Column('last_update', TIMESTAMP, default=datetime.utcnow())
    amount = Column('amount', Integer)

    product = relationship('Product', back_populates='history')


class Warehouse(Base):
    __tablename__ = 'warehouse'
    metadata = metadata
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column('name', String)
    latitude = Column('latitude', Float)
    longitude = Column('longitude', Float)

    user = relationship('User', back_populates='warehouse')
    warehouse_type = relationship('WarehouseType', back_populates='warehouse')
    product_location = relationship('ProductLocation', back_populates='warehouse')
    order = relationship('Order', back_populates='warehouse')
    resource_location = relationship('ResourceLocation', back_populates='warehouse')


class WarehouseType(Base):
    __tablename__ = 'warehouse_type'
    metadata = metadata
    id = Column('id', Integer, primary_key=True, autoincrement=True)
    warehouse_id = Column('warehouse_id', Integer, ForeignKey('warehouse.id'))
    category_id = Column('category_id', Integer, ForeignKey('category.id'))

    warehouse = relationship('Warehouse', back_populates='warehouse_type')
    category = relationship('Category', back_populates='warehouse_type')


class ProductLocation(Base):
    __tablename__ = 'product_location'
    metadata = metadata
    id = Column('id', Integer, primary_key=True, autoincrement=True)
    product_id = Column('product_id', Integer, ForeignKey('product.id'))
    warehouse_id = Column('warehouse_id', Integer, ForeignKey('warehouse.id'))
    product_amount = Column('product_amount', Integer)

    product = relationship('Product', back_populates='product_location')
    warehouse = relationship('Warehouse', back_populates='product_location')


class Equipment(Base):
    __tablename__ = 'equipment'
    metadata = metadata
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String)
    description = Column(String)

    composite = relationship('Composite', back_populates='equipment')


class Composite(Base):
    __tablename__ = 'composite'
    metadata = metadata
    id = Column(Integer, primary_key=True, autoincrement=True)
    employee_id = Column(Integer, ForeignKey('user.id'))
    equipment_id = Column(Integer, ForeignKey('equipment.id'))
    start_at = Column(TIMESTAMP, default=datetime.utcnow())
    end_at = Column(TIMESTAMP, nullable=True)
    resource_id = Column(Integer, ForeignKey('resource.id'))
    resource_amount = Column(Float)
    product_id = Column(Integer, ForeignKey('product.id'))
    product_amount = Column(Integer)

    product = relationship('Product', back_populates='composite')
    equipment = relationship('Equipment', back_populates='composite')
    employee = relationship('User', back_populates='composite')
    resource = relationship('Resource', back_populates='composite')


class Resource(Base):
    __tablename__ = 'resource'
    metadata = metadata
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String)
    description = Column(String)
    unit_id = Column(Integer, ForeignKey('unit.id'))

    composite = relationship('Composite', back_populates='resource')
    resource_location = relationship('ResourceLocation', back_populates='resource')
    recipe = relationship('Recipe', back_populates='resource')
    unit = relationship('Unit', back_populates='resource')


class ResourceLocation(Base):
    __tablename__ = 'resource_location'
    metadata = metadata
    id = Column(Integer, primary_key=True, autoincrement=True)
    resource_id = Column(Integer, ForeignKey('resource.id'))
    warehouse_id = Column(Integer, ForeignKey('warehouse.id'))
    amount = Column(Float)

    warehouse = relationship('Warehouse', back_populates='resource_location')
    resource = relationship('Resource', back_populates='resource_location')


class Recipe(Base):
    __tablename__ = 'recipe'
    metadata = metadata
    id = Column(Integer, primary_key=True, autoincrement=True)
    product_id = Column(Integer, ForeignKey('product.id'))
    resource_id = Column(Integer, ForeignKey('resource.id'))
    amount = Column(Float)

    product = relationship('Product', back_populates='recipe')
    resource = relationship('Resource', back_populates='recipe')

# class Leaving(Base):
#     __tablename__ = 'leaving'
#     metadata = metadata
#     id = Column(Integer, primary_key=True, autoincrement=True)
#     product_id = Column(Integer, ForeignKey('product.id'))
#     warehouse_from_id = Column(Integer, ForeignKey('warehouse.id'))
#     warehouse_to_id = Column(Integer, ForeignKey('warehouse.id'))
#     amount = Column(Integer, default=0)
#     product = relationship('Product', back_populates='leaving')
#
#
# class Arrival(Base):
#     __tablename__ = 'arrival'
#     metadata = metadata
#     id = Column(Integer, primary_key=True, autoincrement=True)
#     product_id = Column(Integer, ForeignKey('product.id'))







