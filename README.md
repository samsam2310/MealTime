# MealTime


## Command

### menu

* new menu_name
* show menu_idx
* del menu_idx
* edit menu_idx item_list ... $ op_list ... $ addition_list ...
	* item: name|price(number)|opidx;opidx;opidx
	* op: name|price(number)
	* addition: name|price(number)

## meal

* new menu_idx start_time stop_time meal_time info_titles...
	* time_format: 2017-09-10-13:15
* show meal_idx
* done meal_idx

### order

* meal_id info_list ... $ item_idx op op op ... $ addi addi addi ... $ message message ...
