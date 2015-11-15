# -*- mode:toml; -*-

"charm"                  = "mysql"

# Define what config options can be modified, these will use
# the existing config's defaults
"allowed_fields"         = ["bind-address",
                            "backup_retention_count",
                            "dataset-size"]

# Ubuntu series this package will support
"series" = ["trusty", "xenial"]

[fields]
# Define options that can be configured during install
# along with setting a default recommended option

# Example, mysql, has options such as bind-address and
# backup_retention_count, make these editable and include
# dataset-size as is and make editable.


# User can change from default 0.0.0.0, we place our own
# recommendation here as well
"bind-address"           = "172.16.0.4"

# Change the backup retention from default of 7 to our
# recommended 5, also configurable at install.
"backup_retention_count" = 5
