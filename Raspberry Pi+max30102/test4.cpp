#include <iostream>
#include <unistd.h>
#include "JS_HeartRate.cpp"
#include<string>
#include"Python.h"
using namespace std;


int main() {
	cout << "Starting..." << endl;
	Py_Initialize();
	cout << "initialized" <<endl;

	PyRun_SimpleString("import sys");
	PyRun_SimpleString("sys.path.append('/home/pi')");
	PyRun_SimpleString("import client");
	PyRun_SimpleString("client.setup()");

	HRSInterface hrs;
	hrs.start();
	cout << "Done." << endl;
	cout << "Began heart rate calculation..." << endl;
	while (1) {
		int numb = hrs.getLatestHeartRate();
		int num = hrs.getSafeHeartRate();
		cout << "IR Heart Rate- Latest:" << numb << ", SAFE:" << num;
		cout << ", Temperature: " << hrs.getLatestTemperatureF() << endl;
		string str1 = "client.send(" + to_string(num) + ")";
		cout << str1 << endl;
		const char* ch = str1.c_str();
		PyRun_SimpleString(ch);
		usleep(1000000);
	}
	PyRun_SimpleString("client.shutdown()");
	Py_Finalize();
	return 0;
}
