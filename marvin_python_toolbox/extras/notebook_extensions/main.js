//    Copyright [2017] [B2W Digital]
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//     http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

define([
    'base/js/namespace',
    'base/js/events',
], function(
    Jupyter,
    events
) {
	"use strict";

	var log_prefix = '[MARVIN]';

    function load_ipython_extension() {
    	
    	var add_marvin_options = function () {
    		var select = $('<select/>').attr("class", "form-control select-xs").attr("id", "marvin_action");
    		select.append($('<option/>'));
    		select.append($('<option/>').attr('value', 'acquisitor').attr("id", "acquisitor").text('Acquisitor and Cleaner'));
    		select.append($('<option/>').attr('value', 'tpreparator').attr("id", "tpreparator").text('Training Preparator'));
    		select.append($('<option/>').attr('value', 'trainer').attr("id", "trainer").text('Trainer'));
    		select.append($('<option/>').attr('value', 'evaluator').attr("id", "evaluator").text('Metrics Evaluator'));
    		select.append($('<option/>').attr('value', 'ppreparator').attr("id", "ppreparator").text('Prediction Preparator'));
    		select.append($('<option/>').attr('value', 'predictor').attr("id", "predictor").text('Predictor'));
            select.append($('<option/>').attr('value', 'feedback').attr("id", "feedback").text('Feedback'));
    		Jupyter.toolbar.element.append(select);
    	};

    	var handler = function () {
    		
    		var cell = Jupyter.notebook.get_selected_cell();
    		if (cell.cell_type != "code"){
    			alert("This is not a python code cell !!!");
    			return;
    		}

    		var marvin_action = document.getElementById("marvin_action");
			if (marvin_action.selectedIndex == 0 && !cell.metadata.marvin_cell){
				marvin_action.focus();
				return;
			}

			if(cell.metadata.marvin_cell){
				marvin_action.options.namedItem(cell.metadata.marvin_cell).disabled = false;
				update_div(cell, cell.metadata.marvin_cell);
				delete cell.metadata.marvin_cell;
				console.log(log_prefix, "Unmark cell %s as marvin_cell!", cell.cell_id);

			}else{
				marvin_action.selectedOptions[0].disabled = true;
				cell.metadata.marvin_cell = marvin_action.selectedOptions[0].value;
				update_div(cell, cell.metadata.marvin_cell);
				console.log(log_prefix, "Mark cell %s as marvin_cell!", cell.cell_id);
			}
        };

        var update_div = function (cell, action){

        	if(cell.input[0].style.borderRight.length == 0){
        		cell.input[0].style.borderRight = "10px solid lightgreen";

        		var action_text = document.getElementById("marvin_action").options.namedItem(cell.metadata.marvin_cell).text;

        		var label = $('<div/>').attr("id", "marvin_" + cell.cell_id).text(action_text);
        		label[0].style = "font-size: smaller; color: gray;";

        		cell.input[0].parentNode.insertBefore(label[0], cell.input[0].nextSibling)

        	}else{
        		cell.input[0].style.borderRight = "";
        		document.getElementById("marvin_" + cell.cell_id).remove();
			}

        	console.log(log_prefix, "updating cell %d", cell.cell_id);
        };

        var initialize_marvin_cells = function () {
	        console.log(log_prefix, 'updating all marvin cells');
	        var cells = Jupyter.notebook.get_cells();
	        
	        for (var i = 0; i < cells.length; i++) {
	            var cell = cells[i];
	            if (cell.cell_type == "code" && cell.metadata.marvin_cell) {
	            	document.getElementById("marvin_action").options.namedItem(cell.metadata.marvin_cell).disabled = true;
	            	update_div(cell, cell.metadata.marvin_cell);
	            }
	        }

	        var cell = Jupyter.notebook.get_selected_cell();
	        if (cell.cell_type != "code"){
        		$('button[data-jupyter-action="marvin_extension:export"]')[0].disabled = true;
        	}

	    };

        events.on("select.Cell", function(event, params){
        	var cell = params.cell;

        	if (cell.cell_type != "code"){
        		$('button[data-jupyter-action="marvin_extension:export"]')[0].disabled = true;
        	}else{
        		$('button[data-jupyter-action="marvin_extension:export"]')[0].disabled = false;
        	}

        	if (cell.cell_type == "code" && cell.metadata.marvin_cell){
        		document.getElementById("marvin_action").value = cell.metadata.marvin_cell;
        	}else{
        		document.getElementById("marvin_action").value = "";
        	}
        });

        events.on("delete.Cell", function(event, params){
        	var cell = params.cell;

        	if (cell.cell_type == "code" && cell.metadata.marvin_cell){
        		document.getElementById("marvin_action").options.namedItem(cell.metadata.marvin_cell).disabled = false;
        	}
        });

        var action = {
            icon: 'fa-code',
            help    : 'Mark and Unmark cell as marvin action. To export code save the notebook.',
            help_index : 'mm',
            handler : handler
        };

        var full_action_name = Jupyter.actions.register(action, 'export', 'marvin_extension');
        
        add_marvin_options();
        Jupyter.toolbar.add_buttons_group([full_action_name]);

        if (Jupyter.notebook !== undefined && Jupyter.notebook._fully_loaded) {
            initialize_marvin_cells();
        }
    }

    return {
        load_ipython_extension: load_ipython_extension
    };
});