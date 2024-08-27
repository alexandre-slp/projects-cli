# Projects-cli

## Dependencies

- Docker
- Git

## Usage

**procli** *[PTIONS]* **COMMAND** *[ARGS]*

## Commands

| Command     |           Explanation           |
|-------------|:-------------------------------:|
| **help**    |    Show available commands.     |
| **install** |    Clone app from git repo.     |
| **list**    | List available apps and status. |
| **remove**  |           remove app            |
| **start**   |            start app            |
| **stop**    |            stop app             |

## Setup

Create a GitHub personal access token (fine-grained) and store it in a local env with the 
format `GITHUB_{ORGANIZATION}_TOKEN` where you should replace `{ORGANIZATION}` with your 
organization name.  
Ex.: `GITHUB_MYORGNAME_TOKEN=abcdef1234`  

This token needs `READ access to code and metadata` permission on all organization repositories
(or the ones you want to manage)