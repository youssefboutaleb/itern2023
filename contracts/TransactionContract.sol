// SPDX-License-Identifier: GPL-3.0

pragma solidity ^0.8.0;

contract EnergyConsumption {
    struct Consomation {
        uint256 time;
        uint256 amount;
    }
    
    mapping(address => string) public users; // Store profile as a string
    mapping(address => Consomation[]) public consomations;
     
    function sendConsomation(uint256 amount) external {
       if (bytes(users[msg.sender]).length == 0) { // Check if user profile is not set
            users[msg.sender] = "standard"; // Set a default profile (you can change this as needed)
        }
        
        consomations[msg.sender].push(Consomation(block.timestamp, amount));
    }

    function sendConsomation_csv(uint256[] memory times, uint256[] memory amounts) external {
        require(times.length == amounts.length, "Array lengths must be equal");
        
        if (bytes(users[msg.sender]).length == 0) { // Check if user profile is not set
            users[msg.sender] = "standard"; // Set a default profile (you can change this as needed)
        }
        
        for (uint256 i = 0; i < times.length; i++) {
            consomations[msg.sender].push(Consomation(times[i], amounts[i]));
        }
    }

    
    
    
    function getConsomation(address user) external view returns (uint256[] memory, uint256[] memory) {
        uint256[] memory times = new uint256[](consomations[user].length);
        uint256[] memory amounts = new uint256[](consomations[user].length);
        
        for (uint256 i = 0; i < consomations[user].length; i++) {
            times[i] = consomations[user][i].time;
            amounts[i] = consomations[user][i].amount;
        }
        
        return (times, amounts);
    }
    
    function updateProfile(address userAddress, string memory newProfile) external  {
        users[userAddress] = newProfile;
    }
    function getProfile(address userAddress) external view returns (string memory) {
        return users[userAddress];
    }

}
