#  this function gets called from the home path in static_paths
# it takes in the path of where the html_file is stored
# and the data I want to display

import secrets
import server.database as db


def render_template(html_filename, data, num_visits, is_password_valid, username):

    with open(html_filename) as html_file:
        template = html_file.read()
        # call the replace_placeholders with the html file as a string, and that data
     #   template = replace_placeholders(template, data)
        
        template = insert_token(secrets.token_urlsafe(15), num_visits)
        template = invalid_password(template, is_password_valid)
        template = render_username_if_authenticated(template, username)
        template = render_loop(template, data)
        
        return template



# def replace_placeholders(template, data):
#     # iterate over all the data
#     replaced_template = template

#     # data.keys() as long as the data is stored as a dictionary
#     for placeholder in data.keys():
#         # print("this is a place holder : ", placeholder)
#         # print("this is data.keys : ", data.keys() )
#         # print("size of dict , ++++++++++ " , len(data.keys()) )
#         if len(data.keys()) == 1:
#             # then we only have a comment
        
#             if placeholder == 'comment':
#                 replaced_template = replaced_template.replace("{{comment}}", data[placeholder])
#             # means user only uploaded an image
#             if placeholder == 'imageName':
#                 replaced_template = replaced_template.replace("{{imageName}}", None)
#         # if the value is a string go to the template and replace the placeholder with the data
#         else:
            
#             if isinstance(data[placeholder], str):
#                 # if_content += replace_if_holders(if_to_else_template, data[placeholder])
#                 # if_content += replace_else_holders(else_to_end_template, data[placeholder])
#                 replaced_template = replaced_template.replace("{{"+placeholder+"}}", data[placeholder])
#     return replaced_template

def replace_if_holders(template, data):
    if_temp = template
    # print("XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX")
    # print("start of if_holders")
    # print(if_temp)
    # print("end of if holders")
    # print("XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX")
    if data == "":
        if_temp = if_temp.replace("{{comment}}", data)
    else:
        if_temp = if_temp.replace("{{comment}}", data)
    return if_temp

def replace_else_holders(template, data):
    else_temp = template

    # print("XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX")
    # print("start of else_holders")
    # print(else_temp)
    # print("end of else_holders")
    # print("XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX")
    if data == "":
        else_temp = ""
       # print("this is the replaced temp if there is no image in the database", else_temp)
    else:
        else_temp = else_temp.replace("{{imageName}}", data)
        #print("this is the replaced temp if there is an image in the database", else_temp)
    return else_temp

def replace_loopholders(template, data):
    loop_template = template
    if_tag = "{{if no_image}}"
    else_tag = "{{else}}"
    end_if_tag = "{{end_if}}"

    if_index = template.find(if_tag)
    else_index = template.find(else_tag)
    end_if_index = template.find(end_if_tag)
    # these are the starting indices for my if, else, and end if tags in the html

    # we need to make separate calls to functions that will handle the if and else blocks
    # then we can concatenate them together and return them 
    if_template = loop_template[if_index + len(if_tag): else_index]
    else_template = loop_template[else_index + len(else_tag) : end_if_index]
    if_content = ""
    for placeholder in data.keys():
        # print("placeholder :",placeholder)
        if len(data.keys()) == 1:
            if placeholder == 'comment':
                if_content += replace_if_holders(if_template, data[placeholder])
                if_content += replace_else_holders(else_template, "")
                
            elif placeholder == 'imageName':
                if_content += replace_if_holders(if_template, "")
            #    if_content += replace_else_holders(else_template, data[placeholder])
                
        # if there is more than one key in the data dictionary menaing there is a comment and an image
        else:
            if placeholder == 'comment':
                if_content += replace_if_holders(if_template, data["comment"] )
            else:
                if_content += replace_else_holders(else_template, data[placeholder])
    # print("this is the loop template", loop_template, '\n\n\n\n\n')
    # print("the if_content", if_content, "\n\n\n\n\n")
    final_loop = loop_template[:if_index] + if_content + loop_template[end_if_index + len(end_if_tag):]
    # print("the final_loop: ", final_loop, "\n\n\n\n\n")
    return final_loop

def render_loop(template, data):
    if "loop_data" in data:
        # print("This is the data in the loop_data. :" , data)
        loop_start_tag = "{{loop}}"
        loop_end_tag = "{{end_loop}}"

        start_index = template.find(loop_start_tag)
        end_index = template.find(loop_end_tag)


        # if_tag = "{{if no_image}}"
        # else_tag = "{{else}}"
        # end_if_tag = "{{end_if}}"

        # if_index = template.find(if_tag)
        # else_index = template.find(else_tag)
        # end_if_index = template.find(end_if_tag)
        # these are the starting indices for my if, else, and end if tags in the html
      
        # this grabs the chunk of the html template where the loop is and where we render
        loop_template = template[start_index + len(loop_start_tag): end_index]
        loop_data = data["loop_data"]

        loop_content = ""
      
        # loop data will contain the comment and the image file
        # loop_data will look like this 
        #         { "comment" : "this is a comment", "imageName" ; coolpichhhfsdfj.jpg}
        #         { "comment" : "another comment"}
        # TODO: find a way to not place all data in the loop. have to examine the replace_placeholders function and how its handling it
        for single_piece_of_content in loop_data:
            # print("this is single piece of content >>>>>>>>>>, ", single_piece_of_content )

            loop_content += replace_loopholders(loop_template, single_piece_of_content)
          
          
        # splice in the new loop_content into the template


        final_content = template[:start_index] + loop_content + template[end_index+len(loop_end_tag):]

        return final_content

    
def insert_token(token, num_visits):
    with open("static/index.html") as html:
        template = html.read()
        token_tag = "{{token_val}}"
        visit_tag = "{{visits}}"
        template = template.replace(token_tag, token).replace(visit_tag, str(num_visits))
    #    template = template.replace(visit_tag, str(num_visits))
        db.store_xsrf_token(token)
        #print(template)
        return template

"""
    if password_match is -1 password is less than 8 characters try again
    if password_match is 0 we know they are trying to register but the passwords dont match
    if password_match is 1 we know they are trying to register and the passwords match!
"""
def invalid_password(template, is_password_valid):
    html_password_matching_tag = "{{not matching password}}"

    # if its -1 or 1 we only need to display an empty string, if the passwords match we are going to 
    # tell the user to login or something
    if is_password_valid == 1:
        print("since there either is a password match, or there isn't even a register dictionary we want to  with a blank string")
        template = template.replace(html_password_matching_tag, "")
        return template
    # if the password is not matching, we display the text they need to try again
    elif is_password_valid == -1:
        print("the password lengths dont match")
        template = template.replace(html_password_matching_tag, "Password needs to be longer than 8 characters try again")
        return template
    elif is_password_valid == 0:
        template = template.replace(html_password_matching_tag, "Password do not match try again")
        return template
    
def render_username_if_authenticated(template, username):
    # we want to render the template with the Welcome username displayed
    welcomeuser = "{{welcome user}}"
    if username == None:
        print("there is not username so there is no valid auth token")
        template = template.replace(welcomeuser, "")
        return template
    else:
        template = template.replace(welcomeuser, f"Welcome back {username.decode()}")
        return template

# if __name__ == '__main__':
    
#     sampleDictList = [{"comment": "this is a 1 comment", "imageName" : "acoolpickrkfkdfk.jpg"}, {"comment": "this 2 is a comment"}]
#     message = { "loop_data": sampleDictList} 
#     num_visits = 10
#     import os
#     print("current directory>>>>>>>>>>>>>>>>",os.getcwd())

#     con = render_template(file, message, num_visits)
#     print('\n\n\n\n\n\n\n')
#     print(con)

