### TODO
 - [ ] Look at apigateway request mapping to raw json, doesn't seem right
 - [ ] Split lambda function into multiple files based on intent
 - [ ] Detect if stop timer is too long (someone forgot to stop), cancel that timer

### secrets
 - Add a `secrets.py` file in the config folder as outlined in `secrets_example.py`

### Run code as module 
 - imports are hard, I don't understand it
 - `python -m source.interactions.list_commands`

### Resources
- https://oozio.medium.com/serverless-discord-bot-55f95f26f743
- https://medium.com/@geoff.ford_33546/creating-a-pynacl-lambda-layer-c3f2e1b6ff11
