	/*
	 * Quick lookup on unique terms using Jsonp
	 * Created by Greg Elin, Chief Data Officer, Federal Communication Commission
	 * License: Public Domain
	 *
	 * REQUIREMENTS
	 *  Jquery 1.4.4
	 *  Expects to find the following HTML form on the page:
	 *  <form id="q_search"></form>
	*/
	
	 function updateResults() {
		$("#q_result").html("");
		q_term = $("#q_term").val();
		q_url = "http://localhost:8080/search/jsonp/"+q_term+"?";
		$.getJSON(q_url+"&callback=?",function(d) {
			if (typeof d.html == "undefined") {
				$("#q_result").html("");
			} else {
				$("#q_result").html(d.html);
			}
		}
		)
	}
	
	/* Initialize settings sliding panel */
	$(document).ready(function(){
		// Set form html
		q_form_html = '<div class="label">Enter identifier<br>Examples: KOLO-TV or SSA</div>\n \
		<input id="q_term" tabindex="1" value=""> \n \
		<div class="label"></div>\n \
		<div id="q_result" style=""></div>';
		
		// Add the HTML to the page
		$("#q_search").html(q_form_html);
		// The following could be used to load a term after page loaded
		// term = $("#q_term").val();
		// Bind the function
		$("#q_term").change(updateResults);
		// Stop form from submitting
		$("form#q_search").submit(function() {
			return false;
		});
	});