# -*- coding:utf-8 -*-


from flask import abort

from api.extensions import db
from api.models.acl import Permission
from api.models.acl import Resource
from api.models.acl import ResourceGroup
from api.models.acl import ResourceGroupItems
from api.models.acl import ResourceType


class ResourceTypeCRUD(object):
    @staticmethod
    def search(q, app_id, page=1, page_size=None):
        query = db.session.query(ResourceType).filter(
            ResourceType.deleted.is_(False)).filter(ResourceType.app_id == app_id)
        if q:
            query = query.filter(ResourceType.name.ilike('%{0}%'.format(q)))

        numfound = query.count()

        return numfound, query.offset((page - 1) * page_size).limit(page_size)

    @classmethod
    def add(cls, app_id, name, perms):
        ResourceType.get_by(name=name, app_id=app_id) and abort(
            400, "ResourceType <{0}> is already existed".format(name))

        rt = ResourceType.create(name=name, app_id=app_id)

        cls.update_perms(rt.id, perms, app_id)

        return rt

    @classmethod
    def update(cls, rt_id, **kwargs):
        rt = ResourceType.get_by_id(rt_id) or abort(404, "ResourceType <{0}> is not found".format(rt_id))
        if 'name' in kwargs:
            other = ResourceType.get_by(name=kwargs['name'], app_id=rt.app_id, to_dict=False, first=True)
            if other.id != rt_id:
                return abort(400, "ResourceType <{0}> is duplicated".format(kwargs['name']))

        if 'perms' in kwargs:
            cls.update_perms(rt_id, kwargs['perms'], rt.app_id)

        return rt.update(**kwargs)

    @classmethod
    def delete(cls, rt_id):
        rt = ResourceType.get_by_id(rt_id) or abort(404, "ResourceType <{0}> is not found".format(rt_id))

        cls.update_perms(rt_id, [], rt.app_id)

        rt.soft_delete()

    @classmethod
    def update_perms(cls, rt_id, perms, app_id):
        existed = Permission.get_by(resource_type_id=rt_id, to_dict=False)
        existed_names = [i.name for i in existed]

        for i in existed:
            if i.name not in perms:
                i.soft_delete()

        for i in perms:
            if i not in existed_names:
                Permission.create(resource_type_id=rt_id,
                                  name=i,
                                  app_id=app_id)


class ResourceGroupCRUD(object):
    @staticmethod
    def search(q, app_id, page=1, page_size=None):
        query = db.session.query(ResourceGroup).filter(
            ResourceGroup.deleted.is_(False)).filter(ResourceGroup.app_id == app_id)

        if q:
            query = query.filter(ResourceGroup.name.ilike("%{0}%".format(q)))

        numfound = query.count()

        return numfound, query.offset((page - 1) * page_size).limit(page_size)

    @staticmethod
    def get_items(rg_id):
        items = ResourceGroupItems.get_by(group_id=rg_id, to_dict=False)

        return [i.resource.to_dict() for i in items]

    @staticmethod
    def add(name, type_id, app_id):
        ResourceGroup.get(name=name, resource_type_id=type_id, app_id=app_id) and abort(
            400, "ResourceGroup <{0}> is already existed".format(name))

        return ResourceGroup.create(name=name, resource_type_id=type_id, app_id=app_id)

    @staticmethod
    def update(rg_id, items):
        existed = ResourceGroupItems.get_by(group_id=rg_id, to_dict=False)
        existed_ids = [i.resource_id for i in existed]

        for i in existed:
            if i.resource_id not in items:
                i.soft_delete()

        for _id in items:
            if _id not in existed_ids:
                ResourceGroupItems.create(group_id=rg_id, resource_id=_id)

    @staticmethod
    def delete(rg_id):
        rg = ResourceGroup.get_by_id(rg_id) or abort(404, "ResourceGroup <{0}> is not found".format(rg_id))

        rg.soft_delete()

        items = ResourceGroupItems.get_by(group_id=rg_id, to_dict=False)
        for item in items:
            item.soft_delete()


class ResourceCRUD(object):
    @staticmethod
    def search(q, app_id, page=1, page_size=None):
        query = db.session.query(Resource).filter(
            Resource.deleted.is_(False)).filter(Resource.app_id == app_id)

        if q:
            query = query.filter(Resource.name.ilike("%{0}%".format(q)))

        numfound = query.count()

        return numfound, query.offset((page - 1) * page_size).limit(page_size)

    @staticmethod
    def add(name, type_id, app_id):
        Resource.get(name=name, resource_type_id=type_id, app_id=app_id) and abort(
            400, "Resource <{0}> is already existed".format(name))

        return Resource.create(name=name, resource_type_id=type_id, app_id=app_id)

    @staticmethod
    def update(_id, name):
        resource = Resource.get_by_id(_id) or abort(404, "Resource <{0}> is not found".format(_id))

        other = Resource.get_by(name=name, resource_type_id=resource.resource_type_id, to_dict=False, first=True)
        if other.id != _id:
            return abort(400, "Resource <{0}> is duplicated".format(name))

        return resource.update(name=name)

    @staticmethod
    def delete(_id):
        resource = Resource.get_by_id(_id) or abort(404, "Resource <{0}> is not found".format(_id))

        resource.soft_delete()



