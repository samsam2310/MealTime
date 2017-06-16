# MealTime


## Command

### group

* new name information_list
* delete id
* join id information_list
* quit id

### menu

* new name
* show idx
* del idx
* edit idx item_list ... $ addition_list ...
	* item: name|price(number)|op;op;op
	* addition: name|price(number)


## meal

* new group_id menu_id start_time stop_time meal_time
* show meal_idx
* done meal_idx

### order

* item_idx op op op ... $ addi addi addi ... $ message message ...
