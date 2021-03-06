# OraxenVerificationBot
# A Discord bot made in Python using Interactions library that allow Polymart buyer verification
# This bot is licensed under the MIT license

import requests
import random
import json
import interactions
import os

# Discord bot variable
token = "REPLACE THIS WITH YOUR BOT ACTUAL TOKEN!"
verified_role_id = 
owner = 
server_id = 
restrict_api_operation_to_owner = 

# Polymart verification variable
base_url = "https://api.polymart.org"
nonce = random.SystemRandom().getrandbits(10)
service = "OraxenVerificationBot"
resource_id = "629"
api_key = None

class PolymartAPI:
   def generateVerifyURL():
       url = base_url + "/v1/generateUserVerifyURL"
       arg = {'service':service,'nonce':nonce}
       token = None
       r = requests.get(url = url, params = arg).json()
       token = r['response']['result']['url']
       return token

   def verifyUser(token):
       url = base_url + "/v1/verifyUser"
       arg = {'service':service,'nonce':nonce,'token':token}
       r = requests.get(url = url, params = arg).json()
       id = r['response']['result']['user']['id']
       return id

   def getUserData(api_key, user_id):
       url = base_url + "/v1/getUserData"
       arg = {'api_key':api_key,'user_id':user_id}
       r = requests.post(url, json=arg).json()
       return r

   def getResourceUserData(api_key, resource_id, user_id):
       url = base_url + "/v1/getResourceUserData"
       arg = {'api_key':api_key,'resource_id':resource_id,'user_id':user_id}
       r = requests.post(url, json=arg).json()
       return r
    
class Init:
    def api_key_init():
        global api_key
        if not api_key and os.path.exists("api_key.dev"):
            api_key_file = open("api_key.dev", "r+")
            api_key = api_key_file.read()
            print("Warning: API Key is read from api_key.dev local file!")

print("Bot Token: " + token)
bot = interactions.Client(token=token)

# Commands

@bot.command(
    name="verify",
    description="Verify your plugin ownership.",
    scope=server_id,
    options = [
        interactions.Option(
            name="token",
            description="User Token of your Polymart account",
            type=interactions.OptionType.STRING,
            required=False,
        ),
    ],
)
async def verify(ctx: interactions.CommandContext, token: str = None):
    await ctx.defer()
    user = ctx.author
    dm = ctx.member
    member = ctx.member
    global api_key
    if ctx.author.roles and verified_role_id in ctx.author.roles:
        await ctx.send(str(user) + " has been already verified!")
        return
    else:
        if not api_key:
            await dm.send("No API keys available for verification! Please contact the server\'s owner immediately.")
            await ctx.send("User " + str(user) + " please check your DM!")
            return
        else:
            if not token:
                token = PolymartAPI.generateVerifyURL()
                await dm.send("**Please login into your Polymart account, then visit this link to get your token. After that run this command again with the token argument to continue the verification process!** \n\n" + token)
                await ctx.send("User " + str(user) + " please check your DM for instructions to get started!")
            else:
                user_id = PolymartAPI.verifyUser(token)
                user_data = PolymartAPI.getUserData(api_key, user_id)
                resource_user_data = PolymartAPI.getResourceUserData(api_key, resource_id, user_id)
                username = user_data['response']['user']['username']
                purchaseValid = resource_user_data['response']['resource']['purchaseValid']
                if not purchaseValid:
                    embed = interactions.Embed(title="Verification Summary for user " + str(ctx.author), description="Username: " + username + "\nUser ID: " + user_id + "\nStatus: Unverified \n\nResult: You didn\'t buy Oraxen on Polymart yet. If you have a license on Spigot instead, you may contact the server\'s moderators to assist in transfering your license to Polymart. After that try verify again! \n\n**IF YOU THINK THIS IS DONE BY ERROR, CONTACT THE SERVER\'S OWNER FOR SUPPORT!**", color=0xab2033)
                    embed.set_footer(text="Verification For User " + str(ctx.author) + " at " + str(datetime.now().strftime("%m-%d-%Y %H:%M:%S")), icon_url=member.user.avatar_url)
                    await ctx.send(embeds=embed)
                    return
                else:
                    purchaseStatus = resource_user_data['response']['resource']['purchaseStatus']
                    if purchaseStatus == "Manual" or purchaseStatus == "Imported":
                        await user.add_role(verified_role_id, server_id)
                        embed = interactions.Embed(title="Verification Summary for user " + str(ctx.author), description="Username: " + username + "\nUser ID: " + user_id + "\nStatus: Verified \n\nResult: You got added to buyer list of the plugin manually. Verified successfully!", color=0x33a343)
                        embed.set_footer(text="Verification For User " + str(ctx.author) + " at " + str(datetime.now().strftime("%m-%d-%Y %H:%M:%S")), icon_url=member.user.avatar_url)
                        await ctx.send(embeds=embed)
                        return
                    else:
                        await user.add_role(verified_role_id, server_id)
                        embed = interactions.Embed(title="Verification Summary for user " + str(ctx.author), description="Username: " + username + "\nUser ID: " + user_id + "\nStatus: Verified \nPaypal Status Code: " + purchaseStatus + "\n\nResult: You have bought the plugin using Paypal. Verified successfully!", color=0x33a343)
                        embed.set_footer(text="Verification For User " + str(ctx.author) + " at " + str(datetime.now().strftime("%m-%d-%Y %H:%M:%S")), icon_url=member.user.avatar_url)
                        await ctx.send(embeds=embed)
                        return

@bot.command(
    name="add_api_key",
    description="Add API Key to Verification Bot (Only for Moderator)",
    default_member_permissions=interactions.Permissions.ADMINISTRATOR,
    scope=server_id,
    options = [
        interactions.Option(
            name="key",
            description="The API Key (generated at polymart.org/account)",
            type=interactions.OptionType.STRING,
            required=True,
        ),
    ],
)
async def add_api_key(ctx: interactions.CommandContext, key: str):
    if restrict_api_operation_to_owner == True and ctx.author.id != owner:
        await ctx.send("The server\'s owner has restricted API operation! Please contact the server\'s owner if you think this is done by error.", ephemeral=True)
    else:
        global api_key
        if not api_key:
            api_key = key
            if os.path.exists("api_key.dev"):
                os.remove("api_key.dev")
                with open('api_key.dev', 'a') as f:
                    f.write(key)
            else:
                with open('api_key.dev', 'a') as f:
                    f.write(key)
            await ctx.send("**API key has been added successfully!** \n\nTo revoke your API key (for security reasons), use the /del_api_key command!", ephemeral=True)
        else:
            await ctx.send("An API key already exist! To revoke this API key, use the /del_api_key command!", ephemeral=True)

@bot.command(
    name="del_api_key",
    description="Delete all added API keys from the Verification Bot (Only for Moderator)",
    default_member_permissions=interactions.Permissions.ADMINISTRATOR,
    scope=server_id
)
async def del_api_key(ctx: interactions.CommandContext):
    if restrict_api_operation_to_owner == True and ctx.author.id != owner:
        await ctx.send("The server\'s owner has restricted API operation! Please contact the server\'s owner if you think this is done by error.", ephemeral=True)
    else:
        global api_key
        if not api_key:
            await ctx.send("There is no API keys added to the bot, nothing to delete!", ephemeral=True)
        else:
            if os.path.exists("api_key.dev"):
                os.remove("api_key.dev")
                api_key = None
                await ctx.send("All API keys are deleted successfully!", ephemeral=True)
            elif not os.path.exists("api_key.dev") and api_key is not None:
                await ctx.send("The API key has been hardcoded to the bot's source code, so the bot has blocked this action. Please contact the server\'s owner if you think this is done by error.", ephemeral=True) 
            elif os.path.exists("api_key.dev") and api_key is not None:
                os.remove("api_key.dev")
                await ctx.send("The API key has been hardcoded to the bot's source code, so the bot has blocked this action. Please contact the server\'s owner if you think this is done by error.", ephemeral=True) 
    

Init.api_key_init()
bot.start()