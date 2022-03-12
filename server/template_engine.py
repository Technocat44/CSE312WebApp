#  this function gets called from the home path in static_paths
# it takes in the path of where the html_file is stored
# and the data I want to display
def render_template(html_filename, data):

    with open(html_filename) as html_file:
        template = html_file.read()
        # call the replace_placeholders with the html file as a string, and that data
        template = replace_placeholders(template, data)
        template = render_loop(template, data)
        return template

def replace_placeholders(template, data):
    # iterate over all the data
    replaced_template = template
    # data.keys() as long as the data is stored as a dictionary
    #TODO: I might not have to use data as a dictionary, I guess it depends
    # I could store the data in variables and pass those along
    for placeholder in data.keys():
        # if the value is a string go to the template and replace the placeholder with the data
        if isinstance(data[placeholder], str):
            replaced_template = replaced_template.replace("{{"+placeholder+"}}", data[placeholder])
    return replaced_template

def render_loop(template, data):
    if "loop_data" in data:
        print("This is the data in the loop_data. :" , data)
        loop_start_tag = "{{loop}}"
        loop_end_tag = "{{end_loop}}"

        start_index = template.find(loop_start_tag)
        end_index = template.find(loop_end_tag)
        
        # this grabs the chunk of the html template where the loop is and where we render
        loop_template = template[start_index + len(loop_start_tag): end_index]
        loop_data = data["loop_data"]

        loop_content = ""
        # loop data will contain the comment and the image file
        for single_piece_of_content in loop_data:
            loop_content += replace_placeholders(loop_template, single_piece_of_content)

        final_content = template[:start_index] + loop_content + template[end_index+len(loop_end_tag):]

        return final_content