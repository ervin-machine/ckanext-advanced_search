import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit
from ckan.logic import get_action
from flask import Blueprint, jsonify
from ckan.common import request

myapi_blueprint = Blueprint("myapi", __name__)

@myapi_blueprint.route("/myapi/search", methods=["GET"])
def hello():
    """Render the advanced_search.html template"""
    return toolkit.render("advanced_search.html")

@myapi_blueprint.route("/myapi/suggestions", methods=["GET"])
def get_suggestions():
    """API route for auto-suggestions"""
    search_query = request.args.get('q', '').strip() 

    if not search_query:
        return jsonify({"error": "Query parameter 'q' is required"}), 400

    suggestions = get_auto_suggestion(search_query)
    return jsonify(suggestions)

def get_auto_suggestion(search_query):
    """Provide auto-suggestions based on dataset titles and tags."""
    query = {
        "q": search_query,
        "rows": 5,
        "fl": "title, tags"
    }

    try:
        response = toolkit.get_action('package_search')({}, query)
        suggestions = set()
        for result in response.get('results', []):
            suggestions.add(result['title'])
            suggestions.update(result.get("tags", []))

        return list(suggestions)
    except Exception as e:
        print(f"Error fetching suggestions: {e}")
        return []

@myapi_blueprint.route("/myapi/dataset/title/<dataset_title>", methods=["GET"])
def get_dataset_by_title(dataset_title):
    """Fetch the dataset metadata by its title"""

    try:
        data_dict = {"q": dataset_title, "rows": 1}
        datasets = get_action("package_search")({}, data_dict)
        
        results = datasets.get('results', [])
        if results:
            dataset = results[0]
            if dataset.get('state') == 'active' and not dataset.get('private'):
                return jsonify(dataset)
            else:
                return jsonify({"error": "Dataset found but is either inactive or private"}), 403  # Forbidden
        else:
            return jsonify({"error": "Dataset not found"}), 404
    except Exception as e:
        print(f"Error fetching dataset: {e}")
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500

@myapi_blueprint.route("/myapi/dataset", methods=["GET"])
def get_datasets_by_tag_or_name():
    """Fetch datasets by tags or name."""
    name = request.args.get('name', '').strip()
    tags = request.args.get('tags', '').strip()

    if not name and not tags:
        return jsonify({"error": "At least one of 'name' or 'tags' is required"}), 400

    query = {
        "q": name if name else "*",
        "rows": 10,
    }

    if tags:
        query['q'] = f"tags:{tags}" 

    try:
        datasets = get_action('package_search')({}, query)

        results = datasets.get('results', [])
        if results:
            return jsonify(results)
        else:
            return jsonify({"error": "No datasets found for the given search criteria"}), 404

    except Exception as e:
        print(f"Error fetching datasets: {e}")
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500



class AdvancedSearchPlugin(plugins.SingletonPlugin):
    plugins.implements(plugins.IConfigurer)
    plugins.implements(plugins.IBlueprint)
    plugins.implements(plugins.ITemplateHelpers)

    def update_config(self, config_):
        """Register templates, public assets, and fanstatic resources"""
        toolkit.add_template_directory(config_, 'templates')
        toolkit.add_public_directory(config_, 'public')
        toolkit.add_resource('fanstatic', 'ckanext-advancedsearch')

    def get_blueprint(self):
        """Register Flask Blueprint routes"""
        return myapi_blueprint

    def before_search(self, search_params):
        """Modify search query for fuzzy search and filtering"""
        search_params['q'] = f"{search_params.get('q', '')}~"

        fq_clauses = search_params.get('fq', '').split()

        if 'bbox' in search_params:
            fq_clauses.append(f"spatial_geom:[{search_params['bbox']}]")

        if 'start_date' in search_params and 'end_date' in search_params:
            fq_clauses.append(f"metadata_created:[{search_params['start_date']} TO {search_params['end_date']}]")

        search_params['fq'] = " ".join(fq_clauses)

        return search_params

    def after_search(self, search_result, search_params):
        """Enhance search results with AI-powered dataset recommendations"""
        return search_result

    def get_helpers(self):
        """Register template helper functions"""
        return {'add_frontend_js': add_frontend_js}


frontend_js = '''
<script>
document.addEventListener("DOMContentLoaded", function() {
    let searchInput = document.getElementById("field-giant-search");
    let suggestionsBox = document.createElement("div");
    suggestionsBox.setAttribute("id", "search-suggestions");
    suggestionsBox.style.position = "absolute";
    suggestionsBox.style.border = "1px solid #ddd";
    suggestionsBox.style.backgroundColor = "#fff";
    suggestionsBox.style.zIndex = "1000";
    searchInput.parentNode.appendChild(suggestionsBox);
    
    searchInput.addEventListener("input", function() {
        let query = searchInput.value;
        if (query.length < 2) {
            suggestionsBox.innerHTML = "";
            return;
        }
        
        fetch(`/api/3/action/auto_suggest?q=${query}`)
            .then(response => response.json())
            .then(data => {
                suggestionsBox.innerHTML = "";
                data.forEach(suggestion => {
                    let suggestionItem = document.createElement("div");
                    suggestionItem.innerText = suggestion;
                    suggestionItem.style.padding = "5px";
                    suggestionItem.style.cursor = "pointer";
                    suggestionItem.addEventListener("click", function() {
                        searchInput.value = suggestion;
                        suggestionsBox.innerHTML = "";
                    });
                    suggestionsBox.appendChild(suggestionItem);
                });
            });
    });
});
</script>
'''

def add_frontend_js():
    """Inject the auto-suggestion JS into CKAN templates."""
    return frontend_js
