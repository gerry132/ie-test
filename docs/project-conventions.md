# Project conventions

## Links to resources and documentation.

- Staging: https://content.ireland.testing.gov.ie/en/
- Pre-prod: https://preprod.content.ireland.testing.gov.ie/en/
- Designs: https://www.figma.com/file/pthp59Uxqm2aU9bqKg5kDh/ireland.ie-Designs?node-id=752%3A4472

## Useful links for help with Wagtail Development

- Slack Channel: https://join.slack.com/t/wagtailcms/shared_invite/zt-yia1fpjn-VTikG53xvuXp~YoENNTZGA
- Learn Wagtail: https://learnwagtail.com/
- Wagtail Official Documentation: https://wagtail.org/
- Django Documentation: https://docs.djangoproject.com/en/4.0/

## StreamField Blocks

There are a large number of stream field block types used throughout the website.

- Wagtail stream field block refs: https://docs.wagtail.org/en/stable/reference/streamfield/blocks.html

BEWARE: if you change stream blocks, new migrations will need to be created. If you rename a stream block or field the content will be lost.

## Page content stream blocks:

[irelandie_utils/blocks.py](../irelandie_utils/blocks.py)

You’ll find a lot of blocks in this file.

At the end of the file are the main StreamBlocks that are included in page models. Some of the blocks are used `inline` on some page model Stream  Fields

## Navigation stream blocks

[irelandie_navigation/blocks.py](../irelandie_navigation/blocks.py)

These blocks are used within Snippet models for the Primary, Secondary and Custom navigation
Snippets

## Snippets

Snippets are django models that are decorated with `@register_snippet`

They are available in the admin in the snippets management section. 

A snippet model can use all valid django model fields as well as Wagtail model fields, including StreamField.

Most snippets are app specific so Navigation snippets are found in the `irelaneir_navigation` app in the models.py file and so on.

Snippets that are aren't app specific are in the `irelandie_utils` app

## Base page model classes

The parent class that all page models ultimately inherit from is: [BasePage](../irelandie_utils/models.py) It's an abstract class and therefore cannot be created in the admin.

Immediate page type models that are in use (pre-production) and inherit from BasePage and can be created in the admin are:

- MissionPage
- MissionSearchPage

There are other abstract page types that inherit from `BasePage`

- HeroPage
- ArticlePage

All other concrete page models (can be created in the admin) are page types that inherit from `HeroPage` or `ArticlePage` or `FreeFormPage`

The `FreeFormPage` inherits from `FreeFormPageBase`(FreeFormPageBase is abstract). It was introduced to allow one stream field to have access to almost all stream blocks. This allowed content editors to arrange the order of all the blocks on a page. Is a page type that can be created as a child of any other page.


## Apps that are waiting for further development

There are a number of apps and/or page types that are not yet fully working. They are in place to support the next phases of development.

- [AlertPageIndex](../irelandie_alerts/models.py)
- [AlertPage](../irelandie_alerts/models.py)
- [ContactDetailPageIndex](../irelandie_contact_details/models.py)
- [ContactDetailPage](../irelandie_contact_details/models.py)
- [CorportateInformationPageIndex](../irelandie_corporate_information/models.py)
- [EventPageIndex](../irelandie_events/models.py)
- [EventPage](../irelandie_events/models.py)
- [CountryGroupPageIndex](../irelandie_missions/models.py)
- [NewsPageIndex](../irelandie_news/models.py)
- [PersonPageIndex](../irelandie_people/models.py)
- [PersonPage](../irelandie_people/models.py)
- [RolePageIndex](../irelandie_people/models.py)
- [RolePage](../irelandie_people/models.py)
- [PlacePageIndex](../irelandie_places/models.py)
- [PlacePage](../irelandie_places/models.py)
- [PressReleasePageIndex](../irelandie_press_releases/models.py)
- [SiteInformationPageIndex](../irelandie_site_information/models.py)
- [SpeechPageIndex](../irelandie_speeches/models.py)

If these page types are brought into service please update the list above.

## Templates

Templates for all content types are located in [../irelandie_project_styleguide/templates](../irelandie_project_styleguide/templates/)

The setup here uses the [django-pattern-library](https://github.com/torchbox/django-pattern-library) which will be available when running in development.

You can access the pattern libray at: http://127.0.0.1:8000/pattern-library

## TODO: list / redundent files

Any code that is currently in use but may need future work is marked with a `TODO:`.

This is a list of files that are not used right now but are still in place for future reference.

- [code_snippet.py](../code_snippet.py)