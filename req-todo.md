
######
### install go tools:

go install github.com/fzipp/gocyclo/cmd/gocyclo@latest
go install github.com/uudashr/gocognit/cmd/gocognit@latest
go install github.com/boyter/scc@latest
go install github.com/golangci/golangci-lint/cmd/golangci-lint@latest
go install golang.org/x/lint/golint@latest

######
### install python dependencies

pip install pyyaml
pip install -r requirements.txt

######
### Run the API 

uvicorn main:app --reload


######
### Validate API Implementation

You can use tools like Spectral to validate that your API implementation matches the specification:


# Install Spectral
npm install -g @stoplight/spectral-cli

# Validate your API against the spec
spectral lint openapi.yaml
