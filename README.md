# MealTime


## Command

### group

* new name information_title_list
* del id
* join id information_list
* quit id

### menu

* new group_idx menu_name
* show group_idx menu_idx
* del group_idx menu_idx
* edit group_idx menu_idx item_list ... $ op_list ... $ addition_list ...
	* item: name|price(number)|opidx;opidx;opidx
	* op: name|price(number)
	* addition: name|price(number)


## meal

* new group_idx menu_idx start_time stop_time meal_time
	* time_format: 2017-09-10-13:15
* show meal_idx
* done meal_idx

### order

* meal_idx item_idx op op op ... $ addi addi addi ... $ message message ...
