# User

* uid: fb uid
* cmd[]: the current cmd and args.
* error_count: int, the times of error input to the cmd.
* udata{}: fb user data cache.

# Menu

* _id: id of menu
* owner: uid of the owner.
* name: name of menu
* items[{ name, price(number), opidxs[] }]: the menu items.
* ops[{ name, price(number) }]: the options for the items of the menu.
* addis[{ name, price(number) }]: the additional options for all the items of the menu.

# Meal

* _id: id of the meal.
* menu_id: _id of the menu.
* owner: uid of owner.
* infos[]: Informations' title of the meal.
* start_time: time.
* stop_time: time.
* meal_time: time.
* fb_csv_id: id of fb csv file.
* is_done(Boolean): is active or not.

# Order

* uid: fb uid
* meal_id: _id of the meal.
* infos[]: Informations' title of the meal.
* order_string: string.
* item_string: string.
* item_price: int.
* addi_idxs[]: int list.
* message: string.