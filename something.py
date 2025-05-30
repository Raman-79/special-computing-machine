import {
  BedrockAgentClient,
  CreateAgentCommand,
  GetAgentCommand,
  paginateListAgents,
} from "@aws-sdk/client-bedrock-agent";

const client = new BedrockAgentClient({ region: "us-east-1" });
