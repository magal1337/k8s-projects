#include <iostream>
#include <cstdlib>
#include "unistd.h"
#include "json.hpp"
#include <fstream>
#include <string>
using json = nlohmann::json;
using namespace std;
void parse_message();
int i;

int main()
{   
    string new_message="False";
    while (new_message=="False"){
        ifstream myfile ("file.json");
        json j;
        myfile >> j;
        new_message=j["env"];
        if (new_message == "True"){
            parse_message();
            std::ofstream o("file.json");
            new_message="False";
            j["env"]="False";
            o << std::setw(4) << j << std::endl;
        }
    
        sleep(5);
    }
}

void parse_message(){
    ifstream msgFile ("message.json");
    json j;
    msgFile >> j;
    std::vector<std::string> routes = j["routes"];
    for (auto &route : routes) {
        std::cout << route << '\n';
    }
    
}