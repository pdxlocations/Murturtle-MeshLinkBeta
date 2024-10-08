import plugins
import plugins.libdiscordutil as DiscordUtil
import xml.dom.minidom
import cfg
import requests
import time

class basicCommands(plugins.Base):

    def __init__(self):
        pass

    def start(self):
        print("[INFO] Loading basic commands")
    
    def onReceive(self,packet,interface,client):
        if(cfg.config["verbose_packets"]):
            print("############################################")
            print(packet)
            print("--------------------------------------------")
        final_message = ""
        if("decoded" in packet):
            
            print("decoded")
            if(packet["decoded"]["portnum"] == "TEXT_MESSAGE_APP"):
                final_message += DiscordUtil.genUserName(interface,packet,details=False)

                text = packet["decoded"]["text"]
                final_message += " > "+text
                
                if(cfg.config["ping_on_messages"]):
                    final_message += "\n||"+cfg.config["message_role"]+"||"

                if(text.startswith(cfg.config["prefix"])):
                    noprefix = text[len(cfg.config["prefix"]):]

                    if(noprefix.startswith("ping")):
                        final_ping = "pong"
                        interface.sendText(final_ping,channelIndex=cfg.config["send_channel_index"])
                        if(cfg.config["send_mesh_commands_to_discord"]):
                                DiscordUtil.send_msg("`MeshLink`> "+final_ping,client,cfg.config)
                    
                    elif (noprefix.startswith("info")):
                        final_info = "<- info ->\n"+"ping\n"+"time\n"+"weather\n"+"hf\n"+"mesh"
                        interface.sendText(final_info,channelIndex=cfg.config["send_channel_index"],destinationId=packet["toId"])
                        if(cfg.config["send_mesh_commands_to_discord"]):
                                DiscordUtil.send_msg("`MeshLink`> "+final_info,client,cfg.config)
                    
                    elif (noprefix.startswith("time")):
                        final_time = time.strftime('%H:%M:%S')
                        interface.sendText(final_time,channelIndex=cfg.config["send_channel_index"],destinationId=packet["toId"])
                        if(cfg.config["send_mesh_commands_to_discord"]):
                            DiscordUtil.send_msg("`MeshLink`> "+final_time,client,cfg.config)
                    
                    elif (noprefix.startswith("weather")):
                        weather_data_res = requests.get("https://api.open-meteo.com/v1/forecast?latitude="+cfg.config["weather_lat"]+"&longitude="+cfg.config["weather_long"]+"&hourly=temperature_2m,precipitation_probability&temperature_unit=fahrenheit&wind_speed_unit=mph&precipitation_unit=inch&timeformat=unixtime&timezone=auto")
                        weather_data = weather_data_res.json()
                        final_weather = ""
                        if (weather_data_res.ok):
                            for j in range(cfg.config["max_weather_hours"]):
                                    i = j+int(time.strftime('%H'))
                                    final_weather += str(int(i)%24)+" "
                                    final_weather += str(round(weather_data["hourly"]["temperature_2m"][i]))+"F "+str(weather_data["hourly"]["precipitation_probability"][i])+"%🌧️\n"
                            final_weather = final_weather[:-1]
                        else:
                            final_weather += "error fetching"
                        print(final_weather)
                        interface.sendText(final_weather,channelIndex=cfg.config["send_channel_index"],destinationId=packet["toId"])
                        if(cfg.config["send_mesh_commands_to_discord"]):
                            DiscordUtil.send_msg("`MeshLink`> "+final_weather,client,cfg.config)
                    
                    elif (noprefix.startswith("hf")):
                        final_hf = ""
                        solar = requests.get("https://www.hamqsl.com/solarxml.php")
                        if(solar.ok):
                            solarxml = xml.dom.minidom.parseString(solar.text)
                            for i in solarxml.getElementsByTagName("band"):
                                final_hf += i.getAttribute("time")[0]+i.getAttribute("name") +" "+str(i.childNodes[0].data)+"\n"
                            final_hf = final_hf[:-1]
                        else:
                            final_hf += "error fetching"
                        print(final_hf)
                        interface.sendText(final_hf,channelIndex=cfg.config["send_channel_index"],destinationId=packet["toId"])

                        if(cfg.config["send_mesh_commands_to_discord"]):
                            DiscordUtil.send_msg("`MeshLink`> "+final_hf,client,cfg.config)
                    
                    
                    elif (noprefix.startswith("mesh")):
                        final_mesh = "<- Mesh Stats ->"

                        # channel utilization
                        nodes_with_chutil = 0
                        total_chutil = 0
                        for i in interface.nodes:
                            a = interface.nodes[i]
                            if "deviceMetrics" in a:
                                if "channelUtilization" in a['deviceMetrics']:
                                    nodes_with_chutil += 1
                                    total_chutil += a['deviceMetrics']["channelUtilization"]

                        if nodes_with_chutil > 0:
                            avg_chutil = total_chutil / nodes_with_chutil
                            avg_chutil = round(avg_chutil, 1)  # Round to the nearest tenth
                            final_mesh += "\n chutil avg: " + str(avg_chutil)
                        else:
                            final_mesh += "\n chutil avg: N/A"
                            
                        if(cfg.config["send_mesh_commands_to_discord"]):
                            DiscordUtil.send_msg("`MeshLink`> "+final_mesh)

                        # # temperature average 
                        # nodes_with_temp = 0
                        # total_temp = 0
                        # for i in interface.nodes:
                        #     a = interface.nodes[i]
                        #     if "environmentMetrics" in a:
                        #         if "temperature" in a['environmentMetrics']:
                        #             nodes_with_temp += 1
                        #             total_temp += a['environmentMetrics']["temperature"]

                        # if nodes_with_temp > 0:
                        #     avg_temp = total_temp / nodes_with_temp
                        #     avg_temp = round(avg_temp, 1)  # Round to the nearest tenth
                        #     final_mesh += "\n temp avg: " + str(avg_temp)
                        # else:
                        #     final_mesh += "\n temp avg: N/A"
                        
                        interface.sendText(final_mesh, channelIndex=cfg.config["send_channel_index"], destinationId=packet["toId"])
                        
                DiscordUtil.send_msg(final_message,client,cfg.config)
            else:
                if(cfg.config["send_packets"]):
                    if((packet["fromId"] == interface.getMyNodeInfo()["user"]["id"]) and cfg.config["ignore_self"]):
                        print("Ignoring self")
                    else:
                        final_message+=DiscordUtil.genUserName(interface,packet)+" > "+str(packet["decoded"]["portnum"])
                DiscordUtil.send_info(final_message,client,cfg.config)
        else:
            final_message+=DiscordUtil.genUserName(interface,packet)+" > encrypted/failed"
            DiscordUtil.send_info(final_message,client,cfg.config)
            print("failed or encrypted")


    def onConnect(interface):
        pass
    
    def onDisconnect(interface):
        pass