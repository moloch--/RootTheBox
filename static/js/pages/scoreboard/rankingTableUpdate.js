//JQuery plugin which provides rankingTableUpdate function to animate the update of a table.
//Note: Requires JQuery 1.4.3 and
//		"Bernie's Better Animation" library (http://berniesumption.com/software/files/2010/09/animator.zip)
//
//Author: Mark Rhodes
//Version: 1.0
//Company: ScottLogic
//Date: 17th November 2010

(function($){
	
	//Defines the 16 standard html colours by they hash codes - if you use others then
	//don't complain when it doesn't work!
	var standardColorNames = {
		aqua: '#00FFFF',
		black: '#000000',
		blue: '#0000FF',
		fuchsia: '#FF00FF',
		gray: '#808080',
		grey: '#808080',
		lime: '#00FF00',
		maroon: '#800000',
		navy: '#000080',
		olive: '#808000',
		purple: '#800080',
		red: '#FF0000',
		silver: '#C0C0C0',
		teal: '#008080',
		white: '#FFFFFF',
		yellow: '#FFFF00'
	};
	
	//Simple non-infallable function to obtain the background color of an element.
	//Assumes that the element and parents are statically positioned, not absolute etc.
	//and works by checking the computed style of an element, if this is transparent
	//recursively looks at colour of the parent node, if no colour is found uses white.
	//Also considers all rgba values to be transparent, so don't use them..
	var getColourOfBackground = function(ele){
		var colorStr = $(ele).css("background-color");
		if(colorStr.indexOf('rgba') === 0 || colorStr === 'transparent'){  //works for 'rgba(0,0,0,0)' in Chrome, Safari and 'transparent' for IE, FF, Opera
			return (ele.parentNode != document) ? getColourOfBackground(ele.parentNode) : '#FFFFFF';
		}
		if(colorStr in standardColorNames){
			colorStr = standardColorNames[colorStr];
		} else if(colorStr.indexOf('#') == -1){ //in case it's already a hex color (occurs in IE).
			colorStr = cssColorToHex(colorStr);
		}
		return colorStr;
	}

	//Convert the rgb value to the hex equivalent..
	var cssColorToHex = function(colorStr){
		var hex = '#';
		$.each(colorStr.substring(4).split(','), function(i, str){
			var h = ($.trim(str.replace(')',''))*1).toString(16);
			hex += (h.length == 1) ? "0" + h : h;
		});
		return hex;
	};

	var getMinLeftValueInOptions = function(options){
		var minLeft = 0;
		$.each(options.animationSettings, function(part, settings){
			minLeft = Math.min(settings.left, minLeft); 
		});
		return minLeft;
	}

	//The default options to use in the case that none as specified..
	var defaultOptions = {
		onComplete: function(){ /*do nothing*/ },
		duration: [1000, 0, 700, 0, 500], //The milliseconds to do each phase and the delay between them
		extractIdFromCell: function(td){ return $.trim($(td).html()); }, //the function to use to extract the id value from a cell in the id column.
		animationSettings: {
			up: {
				left: -25, // Move left
				backgroundColor: '#004400' // Dullish green
			},
			down: {
				left: 25, // Move right
				backgroundColor: '#550000' // Dullish red
			},
			fresh: {
				left: 0, //Stay put in first stage.
				backgroundColor: '#FFFF33' // Yellow
			},
			drop: {
				left: 0, //Stay put in first stage.
				backgroundColor: '#550055' // Purple
			}
		}
	};
	
	//given a cell it removes the padding from it and returns what it was as a string.
	var removeAndReturnPadding = function(td){
		td = $(td);
		var cellPadding = getPadding(td);
		td.css({padding : 0});
		return cellPadding;
	};

	function getPadding(td) {
		return td.css("padding-top") + " " +  td.css("padding-right") + " " + td.css("padding-bottom") + " " +  td.css("padding-left");
	}

	function getMargins(td) {
		return td.css("margin-top") + " " +  td.css("margin-right") + " " + td.css("margin-bottom") + " " +  td.css("margin-left");
	}
	
	//should be given the options passed in from the command-line and
	//fills in any missing parameters with default values.
	var completeOptions = function(options){
		if(!options){
			options = {};
		}
		//Allow some parameters to be given as single values that can be converted to what the
		//rankingTableUpdate function expects..
		if(typeof options.duration ===  'number'){
			var overThree =  options.duration/3;
			//set each phase to take a third of the time with no delay between them..
			options.duration = [overThree, 0, overThree, 0, overThree];
		}

		//set any unset parameters to the default values..
		return $.extend(true, {}, defaultOptions, options);
	}

	//Replaces the first element is "this" jQuery object, which should be an HTML table,
	//with the given new version and animates the changes based on the given options.
	//
	//params:
	//	newTable - an HTML table element or jQuery object in which the first element is
	//             an HTML table
	//  options - a JS object which defines how the animation should operate.
	$.fn.rankingTableUpdate = function(newTable, options){
		//make sure we have jQuery wrapped versions of both tables..
		var jOrigTable = this, jNewTable = $(newTable);
		
		//store a reference to the actual tables that will be updated..
		var origTable = this[0];
		newTable = jNewTable[0];
		
		//we need the new table to be hidden and have the same parent as the orig table,
		//so we can measure it and get colour values from it accurately..
		jNewTable.hide();
		var jOrigTableParent = jOrigTable.parent();
		if(jNewTable.parent()[0] !== jOrigTableParent[0]){
			jOrigTableParent.append(newTable);
		}
		
		//fills in any blank options will default values so as to simplify this function's code..
		options = completeOptions(options);

		//store references to the tbodies and "cache" some values..
		var origTBody = origTable.tBodies[0];
		var newTBody = newTable.tBodies[0];
		var rowsInNewTable = newTBody.rows.length; //cache this as it's slow in IE.
		var columnsInEachRow = origTable.tHead.rows[0].cells.length;
		var colourBehindTable = getColourOfBackground(origTable.parentNode);

		//both tables should have the same columns, we need to examine
		//these and figure out which columns need to be updated..
		//columns should have class either anim:position, anim:constant, anim:id, or anim:update.
		var idColumn = 0, positionColumns = new Array(); constantColumns = {}, updatingColumns = {}, noUpdatingColumns = true;
		$(origTable.tHead.rows[0].cells).each(function(i, td){
			td = $(td);
			if(td.hasClass("anim:position")){ 
				positionColumns.push(i);
				updatingColumns[i] = true;
			} else if(td.hasClass("anim:id")){
				idColumn = i;
				constantColumns[i] = true;
			} else if(td.hasClass("anim:constant")){
				constantColumns[i] = true;
			} else {  //by default treat as an updating column..
				updatingColumns[i] = true;
				noUpdatingColumns = false;
			}
		});

		//associate the value of the id column for the table with the row in which is appears..
		var origTableIdsToRows = {}, newTableIdsToRows = {};
		$(origTBody.rows).each(function(row, tr){ 
			origTableIdsToRows[options.extractIdFromCell(tr.cells[idColumn])] = row;
		});
		$(newTBody.rows).each(function(row, tr){ 
			newTableIdsToRows[options.extractIdFromCell(tr.cells[idColumn])] = row;
		});
	
		//break the id's in five sets - up, down, fresh, drop, stayPut
		var up = {}, down = {}, fresh = {}, drop = {}, stayPut = {};
		var maxRowsUp = 0, maxRowsDown = 0, numRowsStaying = 0;
		$.each(origTableIdsToRows, function(id, oldRow){
			//case that a the row needs to be moved..
			if(id in newTableIdsToRows){
				var newRow = newTableIdsToRows[id];
				var diff = oldRow - newRow;
				if(diff > 0){
					up[oldRow] = newRow;
					maxRowsUp = Math.max(diff, maxRowsUp);
				} else if(diff < 0){
					down[oldRow] = newRow;
					maxRowsDown = Math.max(0-maxRowsDown, maxRowsDown)
				} else {
					stayPut[oldRow] = true;
					numRowsStaying++;
				}
				delete newTableIdsToRows[id];
			} else {
				drop[oldRow] = true;
			}
		});
		//elements left in the new table must be new ones..
		$.each(newTableIdsToRows, function(id, newRow){
			//need to make the new unique from anything in the other objects..
			fresh['x'+newRow] = true;
		});
	
		//don't bother doing anything if all rows are staying put and no columns are updating..
		if(numRowsStaying === rowsInNewTable && noUpdatingColumns){
			//wait a little while then do it (in case program is expecting it to take sometime..
			setTimeout(function(){
				//perform the actual swap
				jOrigTable.replaceWith(jNewTable);
				jNewTable.show();

				//run the onComplete callback function..
				options.onComplete();
			}, 10); 
			return;
		}
		
		//--- Animation setup ------
		
		//we need to store the heights of the tables so that we can animate any differences between them..
		var origHeight = jOrigTable.height();
		var origMargins = getMargins(jOrigTable);
		var newHeight = jNewTable.height();
		var minLeftValue = getMinLeftValueInOptions(options);
	
		//we first wrap the table in a wrapper div that will hide any extra rows we add to it
		//A bit of trickery is required here, to move the table to the right the first, then move
		//the wrapper to the left the same amount, this is because setting overflow: hidden or (even just
		//for overflow-y: hidden!) prevents an inner element extending the left hand side of the container.
		jOrigTable.css({position: "relative", left: 0-minLeftValue });
		
		jOrigTable.wrap(
			$("<div />", {
				css: {
					height: origHeight,
					overflow: "visible",
					position: "relative",
					left: minLeftValue,
					margin: origMargins,
				}
			})
		);

		//wrap table cell contents with a div..
		$(origTBody.rows).each(function(row, tr){
			var row_height = $(tr).height() - 9 + "px";  //TODO - figure out what this difference is.. padding, margins, line height?
			$.each(tr.cells, function(column, td){
				var wrapper = $('<div/>', {
					'class' : 'moveable',
					css: {
						position: "relative",
						padding: removeAndReturnPadding(td),
						height: row_height,
					}
				});
				if(!$(td).hasClass("anim:hold")){	
					wrapper.css("line-height", row_height);
				}
				wrapper.data("row", row);
				wrapper.data("column", column);
				$(td).wrapInner(wrapper);
			});
		});

		var rowDiff = rowsInNewTable - origTBody.rows.length;
		//we'll attach empty extra rows to the end of the table which will be used to hold
		//data latter and will stop fresh rows at the bottom from showing up.
		if(rowDiff > 0){
			var emptyRow = $('<tr/>');
			//put something in first cell to ensure height is ok.
			emptyRow.append($('<td/>', {
				css: {
					color: colourBehindTable,
					backgroundColor: colourBehindTable
				}
			}).html('a'));
			for(var i = 1; i < columnsInEachRow; i++){
				emptyRow.append($('<td/>', {
					css: {
						backgroundColor: colourBehindTable
					}
				}));
			}
			jOrigTable.append(emptyRow);

			while(rowDiff > 0){
				//append a clone so that there is an extra empty row in the table..
				var emptyClone = emptyRow.clone();
				jOrigTable.append(emptyClone);
				rowDiff--;
			}
		}

		//Now do the same for the fresh rows, for these we'll:
		//  1. Clone the row in the new table.
		//  2. Attach the clone to the end of the original table
		//  3. Wrap the cells with divs like above
		$.each(fresh, function(row){
			//the row which the fresh row will move to..
			row = row.substring(1)*1;
			var clone = $(newTBody.rows[row]).clone();
			jOrigTable.append(clone);
			$(clone[0].cells).each(function(column, td){
				var wrapper = $('<div />', {
					'class' : 'moveable',
					css: {
						position: "relative",
						padding: removeAndReturnPadding(td),
						backgroundColor: options.animationSettings.fresh.backgroundColor,
						left: options.animationSettings.fresh.left
					}
				});
				//need to make the row unique so that it doesn't clash..
				wrapper.data("row", 'x'+row);
				wrapper.data("column", column);
				$(td).wrapInner(wrapper);
			});
		});

		//Set up a simple animator chain as the AnimatorChain in animator.js seems to be buggy..
		
		//The third animator should set the table to the state of the new table, this involves showing
		//the new values, shrinking the table if required and pushing the rows left/right so they
		//are back in the table.
		//When it's finished it should perform the switch between the tables.
		var thirdAnimator = new Animator({
			//when it's finished update the table as expected and tidy up..
			onComplete: function(){
				//perform the actual swap (note we replace parentNode which is the table wrapper)..
				$(origTable.parentNode).replaceWith(jNewTable);
				jNewTable.show();

				//run the onComplete callback function..
				options.onComplete();
			},
			duration: options.duration[4]
		});
		
		//In the second phase the rows should be moved verically to their required positions.
		var secondAnimator = new Animator({
			onComplete: function(){
				//play final phase animation after specified delay..
				setTimeout(function(){
					thirdAnimator.play();
				}, options.duration[3]);
			},
			duration: options.duration[2]
		});
		
		//In the initial stage of the animation the updating values should be hidden, the rows coloured
		//and pulled to the left/right as expected and the table extended to accommodate new rows.
		//When complete the values which were hidden are altered to their new ones.
		var updateValue = [];  	//the divs with the values we'll change to the new values.
		var firstAnimator = new Animator({
			onComplete: function(){
				//Update values should contain pairs, the dom element to update and the new
				//value to use, which is a string which may encode dom elements if required..
				$.each(updateValue, function(i, elemAndValue){
					$(elemAndValue[0]).html(elemAndValue[1]);
				});
				
				//play the second animation after specified delay..
				setTimeout(function(){
					secondAnimator.play()
				}, options.duration[1]);
			},
			duration: options.duration[0]
		});

		//if we need to make the table bigger do this at the start of the animation..
		if(origHeight < newHeight){
			firstAnimator.addSubject(new NumericalStyleSubject(origTable.parentNode, "height", origHeight, newHeight));

		} else if(origHeight > newHeight) { //if the table needs to shrink, do this at the end.
			thirdAnimator.addSubject(new NumericalStyleSubject(origTable.parentNode, "height", origHeight, newHeight));
		}

		jOrigTable.find('div.moveable').each(function(i, wrapper){
	
			var newCell; //this will be set to the cell in the new table which is equivalent to the one being
						//wrapped, this will be remain null for wrappers in fresh and dropped rows.
			var oldCell = wrapper.parentNode;
			var row = $(wrapper).data("row");
			var column = $(wrapper).data("column");

			//need to fix the colour so that it really looks like the rows are moving out of place..
			if(!(row in stayPut) && !(row in fresh)){
				var initialBGColor = getColourOfBackground(oldCell);
				$(wrapper).css('background-color', initialBGColor);
				$(wrapper.parentNode).css('background-color', colourBehindTable);
				
			}

			if(row in up){
				var animationSetting = options.animationSettings.up;
				var rowsUp = row-up[row];
				
				var animateToBGColor = animationSetting.backgroundColor;
				var animateLeft = animationSetting.left;
				newCell = newTBody.rows[up[row]].cells[column];
				
				//move it left/right and change the background color..
				firstAnimator.addSubject(new NumericalStyleSubject(wrapper, "left", 0, animateLeft));
				firstAnimator.addSubject(new ColorStyleSubject(wrapper, "background-color", initialBGColor, animateToBGColor)); 
				
				//move the row up..
				var topDiff =  $(origTBody.rows[up[row]]).position().top - $(origTBody.rows[row]).position().top;
				secondAnimator.addSubject(new NumericalStyleSubject(wrapper, "top", 0, topDiff));

				//move it back into position and colour the background to the new cell's colour..
				thirdAnimator.addSubject(new NumericalStyleSubject(wrapper, "left", animateLeft, 0));
				thirdAnimator.addSubject(new ColorStyleSubject(wrapper, "background-color", animateToBGColor, getColourOfBackground(newCell))); 
	
			} else if(row in down){
				var animationSetting = options.animationSettings.down;
				var rowsDown = down[row]-row;
				
				var animateToBGColor = animationSetting.backgroundColor;
				var animateLeft = animationSetting.left;
				newCell = newTBody.rows[down[row]].cells[column];

				//move it left/right and change the background color..
				firstAnimator.addSubject(new NumericalStyleSubject(wrapper, "left", 0, animateLeft));
				firstAnimator.addSubject(new ColorStyleSubject(wrapper, "background-color", initialBGColor, animateToBGColor));
				$(wrapper.parentNode).css('background-color', colourBehindTable);
				
				//move the row down..
				var topDiff = $(origTBody.rows[down[row]]).position().top - $(origTBody.rows[row]).position().top;
				secondAnimator.addSubject(new NumericalStyleSubject(wrapper, "top", 0, topDiff));
	
				//move it back into position and colour the background to the new cell's colour..
				thirdAnimator.addSubject(new NumericalStyleSubject(wrapper, "left", animateLeft, 0));
				thirdAnimator.addSubject(new ColorStyleSubject(wrapper, "background-color", animateToBGColor, getColourOfBackground(newCell)));

			}  else if(row in drop){
				var animationSetting = options.animationSettings.drop;
				
				var animateToBGColor = animationSetting.backgroundColor;
				var animateLeft = animationSetting.left;
				$(wrapper.parentNode).css('background-color', colourBehindTable);
				
				//move it left/right and change the background color..
				firstAnimator.addSubject(new NumericalStyleSubject(wrapper, "left", 0, animateLeft));
				firstAnimator.addSubject(new ColorStyleSubject(wrapper, "background-color", initialBGColor, animateToBGColor));
			
				//move it to the bottom of the table, where it'll be hidden and fade it away.
				var topDiff = newHeight-$(origTBody.rows[row]).position().top;
				secondAnimator.addSubject(new NumericalStyleSubject(wrapper, "top", 0, topDiff));
				secondAnimator.addSubject(new NumericalStyleSubject(wrapper, "opacity", 1, 0, ""));

			} else if(row in fresh){
				//turn row into a number and lose the preceding 'x'..
				row = row.substring(1)*1;

				var animationSetting = options.animationSettings.fresh;
				newCell = newTBody.rows[row].cells[column];

				//move the row up..
				var topDiff = $(origTBody.rows[row]).position().top - $(wrapper.parentNode).position().top;
				secondAnimator.addSubject(new NumericalStyleSubject(wrapper, "top", 0, topDiff));						
				
				//move it back into position and colour the background to the new cell's colour..
				thirdAnimator.addSubject(new ColorStyleSubject(wrapper, "background-color", animationSetting.backgroundColor, getColourOfBackground(newCell)));
				thirdAnimator.addSubject(new NumericalStyleSubject(wrapper, "left", animationSetting.left, 0));

			} else {  //must be in stay put..
				newCell = newTBody.rows[row].cells[column];
			}
			
			//in this case we may need to animate the updating of the value..
			if(column in updatingColumns && (($.inArray(column, positionColumns) != -1) || !(row in stayPut))){
	
				//need to inner wrapper which will allow content of cell to be removed..
				$(wrapper).wrapInner($('<div />', {'class': 'innerWrapper'}));
				var innerWrapper =  $(wrapper).find(".innerWrapper")[0]; //note: this seems like excessive work but there
																		//seems to be a bug with jQuery requiring it to be like this!
				firstAnimator.addSubject(new NumericalStyleSubject(innerWrapper, "opacity", 1, 0, ""));
				if(newCell != null){
					thirdAnimator.addSubject(new NumericalStyleSubject(innerWrapper, "opacity", 0, 1, ""));
					updateValue.push([innerWrapper, $(newCell).html()]);
				}
			}
		});

		//trigger the animation..
		firstAnimator.play();
		
		//make it chainable..
		return this;
	}

})(jQuery);


