resource TestPluginEnableCampaign {
   permissions = ["read", "write"];
   roles = ["user"];
   "read" if "user";
}
