from sqlalchemy import (
    Column, ForeignKey, Integer, String,
    Text, TIMESTAMP, DECIMAL, UniqueConstraint,
    Enum, MetaData, Boolean, Float, Date, event
)
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
import enum
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

    # def update(self):
    #     self.last_updated = datetime.utcnow()
    #     return self.id


# @event.listens_for(Product, 'before_update')
# def before_update_listener(mapper, connection, target):
#     target.last_updated = datetime.utcnow()


class Unit(Base):
    __tablename__ = 'unit'
    metadata = metadata
    id = Column(Integer, primary_key=True, autoincrement=True)
    code = Column('code', String, unique=True)
    name = Column('name', String)


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
    last_updated = Column('last_updated', TIMESTAMP(), default=datetime.utcnow())
    image = Column('image', String, nullable=True)


class Role(Base):
    __tablename__ = 'role'
    id = Column(Integer, primary_key=True, autoincrement=True)
    metadata = metadata
    name = Column('name', String)
    description = Column('description', String)


class UserRoles(Base):
    __tablename__ = 'user_role'
    id = Column(Integer, primary_key=True, autoincrement=True)
    metadata = metadata
    user_id = Column('user_id', Integer, ForeignKey('user.id'))
    role_id = Column('role_id', Integer, ForeignKey('role.id'))


class Category(Base):
    __tablename__ = 'category'
    id = Column(Integer, primary_key=True, autoincrement=True)
    metadata = metadata
    name = Column('name', String)
    description = Column('description', String)


class OrderDetail(Base):
    __tablename__ = 'order_detail'
    id = Column(Integer, primary_key=True, autoincrement=True)
    metadata = metadata
    costumer = Column('costumer', Integer, ForeignKey('costumer.id'))
    paid = Column('paid', Float)
    total_price = Column('total_price', Float)
    user_id = Column('user_id', Integer, ForeignKey('user.id'))
    created_at = Column('created_at', TIMESTAMP(), default=datetime.utcnow())
    is_active = Column('is_active', Boolean, default=True)


class Order(Base):
    __tablename__ = 'order'
    id = Column(Integer, primary_key=True, autoincrement=True)
    metadata = metadata
    product_id = Column('product_id', Integer, ForeignKey('product.id'))
    warehouse_id = Column('warehouse_id', Integer, ForeignKey('warehouse.id'))
    order_detail_id = Column('order_detail_id', Integer, ForeignKey('order_detail.id'))
    count = Column('count', Integer)


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


class Warehouse(Base):
    __tablename__ = 'warehouse'
    metadata = metadata
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column('name', String)
    latitude = Column('latitude', Float)
    longitude = Column('longitude', Float)


class WarehouseType(Base):
    __tablename__ = 'warehouse_type'
    metadata = metadata
    id = Column('id', Integer, primary_key=True, autoincrement=True)
    warehouse_id = Column('warehouse_id', Integer, ForeignKey('warehouse.id'))
    category_id = Column('category_id', Integer, ForeignKey('category.id'))


class ProductLocation(Base):
    __tablename__ = 'product_location'
    metadata = metadata
    id = Column('id', Integer, primary_key=True, autoincrement=True)
    product_id = Column('product_id', Integer, ForeignKey('product.id'))
    warehouse_id = Column('warehouse_id', Integer, ForeignKey('warehouse.id'))
    product_amount = Column('product_amount', Integer)


class ProductHistory(Base):
    __tablename__ = 'product_history'
    metadata = metadata
    id = Column('id', Integer, primary_key=True, autoincrement=True)
    product_id = Column('product_id', Integer, ForeignKey('product.id'))
    warehouse_old_id = Column('warehouse_old_id', Integer, ForeignKey('warehouse.id'))
    warehouse_new_id = Column('warehouse_new_id', Integer, ForeignKey('warehouse.id'))
    last_update = Column('last_update', TIMESTAMP, default=datetime.utcnow())
    amount = Column('amount', Integer)




