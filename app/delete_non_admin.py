from django.contrib.auth import get_user_model

User = get_user_model()

DRY_RUN = True # DO NOT RUN AS FALSE ON PROD....EVER!!!!
INCLUDE_INACTIVE = True

qs = User.objects.filter(is_superuser=False)
if not INCLUDE_INACTIVE:
    qs = qs.filter(is_active=True)

total = User.objects.count()
to_delete = qs.count()

print(f"Total users: {total}")
print(f"Users to DELETE (not Administrator/superuser): {to_delete}\n")


def delete_non_admin():
    for u in qs.values("id", "username", "email"):
        print(f"- id={u['id']} username={u['username']} email={u['email']}")

    if not DRY_RUN and to_delete:
        for i in qs:
            print(i)
            i.delete()
    else:
        print("\nDRY RUN ONLY. Set DRY_RUN=False to actually delete.")
