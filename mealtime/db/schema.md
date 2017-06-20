# User

* uid: fb uid
* cmd[]: the current cmd and args.
* error_count: int, the times of error input to the cmd.


# Group

* _id: id of group
* name: group name
* owner: uid of owner
* info_names[]: The field name of the informations.


# GroupRelation

* uid: fb uid of user
* gid: _id of group
* info[]: Informations of the orders of the group.


# Menu

* _id: id of menu
* gid: _id of the group the menu belone to.
* items[{ name, price(number), ops[] }]: the menu items.
* ops[{ name, price(number) }]: the options for the items of the menu.
* addi[{ name, price(number) }]: the additional options for all the items of the menu.

# Meal

* _id: id of the meal.
* gid: _id of the group.
* menu_id: _id of the menu.
* start_time: time.
* stop_time: time.
* meal_time: time.

# Order

* uid: fb uid
* meal_id: _id of the meal.
* order_string: string.
* message: string.