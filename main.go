package main

import (
	osuParseMpLinks "osuParseMpLinks/osu_api_usage"
)

func main() {

	print("Hellow\n")
	client := osuParseMpLinks.NewHttpClient()
	client.UpdateToken()
	client.GetUserDataByUsernameOrId("9109550")
	print("Hellow\n")

}
