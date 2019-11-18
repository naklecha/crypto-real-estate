pragma solidity ^0.5.0;

contract CRE {
    struct Land{
        uint region;
        uint x;
        uint y;
        address owner;
        uint price;
        uint status;
    }
    mapping(address => uint) public wallet;
    mapping(uint => Land) public land_record;
    uint public landCount = 0;
    uint public check = 0;

    function initLand(uint region, uint x, uint y) public {
        require(check==0, "Already Created Land Grid");
        addLandRecord(region,x,y);
    }
    function addLandRecord (uint i,uint j,uint k) private {
        landCount ++;
        land_record[landCount] = Land(i, j, k, msg.sender, 0, 0);
    }
    function doneInit () public {
        check = 1;
    }

    
    function buyLand (uint landid, uint price) public {
        require(land_record[landid].status == 0,"Not for sale.");

        require(land_record[landid].owner != msg.sender,"You already own it.");

        require(land_record[landid].price <= wallet[msg.sender],"Insufficient funds.");

        require(land_record[landid].price == price,"Price has been changed check the new price.");

        wallet[msg.sender] -= land_record[landid].price;
        wallet[land_record[landid].owner] += land_record[landid].price;
        land_record[landid].owner = msg.sender;
        land_record[landid].status = 1;
    }

    function sellLand (uint landid, uint price) public {
        require(land_record[landid].owner == msg.sender,"You are not authorized to sell this piece of land.");

        land_record[landid].price = price;
        land_record[landid].status = 0;
    }
}