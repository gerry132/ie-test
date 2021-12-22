# -*- coding: utf-8 -*-
import json
import random
import string
from pathlib import Path

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.core.management.base import BaseCommand
from django.db import transaction

from wagtail.core.models import (
    Collection,
    GroupCollectionPermission,
    GroupPagePermission,
    Page,
)
from wagtail.documents.models import Document
from wagtail.images.models import Image as WagtailImage

from irelandie_alerts.models import AlertPage, AlertPageIndex
from irelandie_contact_details.models import ContactDetailPage, ContactDetailPageIndex
from irelandie_corporate_information.models import (
    CorportateInformationPage,
    CorportateInformationPageIndex,
)
from irelandie_events.models import EventPage, EventPageIndex
from irelandie_images.models import CustomImage
from wagtail_localize.models import LocaleSynchronization
from wagtail_localize.synctree import PageIndex
from irelandie_missions.models import CountryGroupPageIndex, CountryPage, MissionPage
from irelandie_news.models import NewsPage, NewsPageIndex
from irelandie_people.models import PersonPage, PersonPageIndex, RolePage, RolePageIndex
from irelandie_places.models import PlacePage, PlacePageIndex
from irelandie_press_releases.models import PressReleasePage, PressReleasePageIndex
from irelandie_publications.models import PublicationPage, PublicationPageIndex
from irelandie_site_information.models import (
    SiteInformationPage,
    SiteInformationPageIndex,
)


def _create_user(username, password, superuser=False):
    user_model = get_user_model()
    user_data = dict()
    user_data[user_model.USERNAME_FIELD] = username
    user_data["email"] = "test@example.com"
    user_data["password"] = password
    if superuser:
        return user_model.objects.create_superuser(**user_data)
    return user_model.objects.create_user(**user_data)


page_types = [
    {"parent": AlertPageIndex, "child": AlertPage},
    {"parent": ContactDetailPageIndex, "child": ContactDetailPage},
    {"parent": CorportateInformationPageIndex, "child": CorportateInformationPage},
    {"parent": EventPageIndex, "child": EventPage},
    {"parent": NewsPageIndex, "child": NewsPage},
    {"parent": PersonPageIndex, "child": PersonPage},
    {"parent": RolePageIndex, "child": RolePage},
    {"parent": PlacePageIndex, "child": PlacePage},
    {"parent": PressReleasePageIndex, "child": PressReleasePage},
    {"parent": PublicationPageIndex, "child": PublicationPage},
    {"parent": SiteInformationPageIndex, "child": SiteInformationPage},
]
content_index_page_types = [p["parent"] for p in page_types]


letters = string.ascii_lowercase


def _get_random_title():
    return "".join(random.choice(letters) for i in range(10))


def _create_index_page(parent, class_, title):
    index_page = class_(title=title)
    parent.add_child(instance=index_page)
    index_page.save_revision()
    return index_page


class Command(BaseCommand):
    def __init__(self, *args, **kwargs):
        self.data_path = Path(settings.PROJECT_DIR) / "irelandie_utils" / "test_data"
        super().__init__(*args, **kwargs)

    def add_arguments(self, parser):
        parser.add_argument(
            "number",
            type=int,
            help="Number of items to create for each mission/page type",
        )

    def create_hierarchy(self):
        with open(self.data_path / "countries.json") as jsonfile:
            countries = json.load(jsonfile)
        home_page = Page.objects.get(slug="home")
        for region in countries:
            region_index_page = _create_index_page(
                home_page, CountryGroupPageIndex, region["region"]
            )
            for country in region["countries"]:
                country_index_page = _create_index_page(
                    region_index_page, CountryPage, country["name"]
                )

                missions = [
                    country["name"] + " Mission 1",
                    country["name"] + " Mission 2",
                ]
                for mission in missions:
                    mission_index_page = _create_index_page(
                        country_index_page, MissionPage, mission
                    )
                    for page_type in content_index_page_types:
                        _create_index_page(
                            mission_index_page, page_type, page_type.__name__
                        )

    def create_users_and_groups(self):
        _create_user("superuser", "superduper", superuser=True)
        indexes = MissionPage.objects.all()
        for index in indexes:
            user = _create_user(index.slug, index.slug)
            group = Group.objects.create(name=index.title)
            group.permissions.add(
                Permission.objects.get(
                    content_type__app_label="wagtailadmin",
                    codename="access_admin",
                )
            )
            root_collection = Collection.get_first_root_node()
            collection = root_collection.add_child(name=index.slug)
            user.groups.add(group)
            for permission_type in ["add", "edit", "publish"]:
                GroupPagePermission.objects.create(
                    group=group,
                    page=index,
                    permission_type=permission_type,
                )
            image_permissions = Permission.objects.all().filter(
                content_type=ContentType.objects.get_for_model(WagtailImage)
            )
            for permission_type in image_permissions:
                GroupCollectionPermission.objects.create(
                    group=group,
                    collection=collection,
                    permission=permission_type,
                )
            document_permissions = Permission.objects.all().filter(
                content_type=ContentType.objects.get_for_model(Document)
            )
            for permission_type in document_permissions:
                GroupCollectionPermission.objects.create(
                    group=group,
                    collection=collection,
                    permission=permission_type,
                )

    def create_fake_page(self, parent, child_type):
        title = _get_random_title()
        fake_page = child_type(title=title)
        parent.add_child(instance=fake_page)
        fake_page.save_revision().publish()
        print("published fake page " + title)

    def create_fake_pages(self, number):
        for page_type in page_types:
            for parent in page_type["parent"].objects.all():
                for _ in range(number):
                    self.create_fake_page(parent, page_type["child"])

    def sync_locale_trees(self):
        # wagtail runs after_create_page() hooks at the view layer
        # rather than the model layer
        # so we need to sync the new pages to other synced locales
        # when we create objects programatically
        page_index = PageIndex.from_database().sort_by_tree_position()
        for locale_sync in LocaleSynchronization.objects.all():
            locale_sync.sync_trees(page_index=page_index)

    @transaction.atomic
    def handle(self, **options):
        self.stdout.write("Importing init data...")

        CustomImage.objects.all().delete()
        CountryGroupPageIndex.objects.all().delete()
        user_model = get_user_model()
        user_model.objects.all().delete()
        Group.objects.all().delete()
        GroupCollectionPermission.objects.all().delete()
        Collection.objects.all().exclude(name="Root").delete()

        self.create_hierarchy()
        self.create_users_and_groups()
        self.create_fake_pages(options["number"])
        self.sync_locale_trees()

        self.stdout.write("...Done")
