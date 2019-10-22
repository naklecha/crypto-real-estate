pragma solidity 0.4.24;

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
    constructor() public {
        uint c = 0;
        for(uint i=0;i<4;i++)
        {
            for(uint j=0;j<64;j++)
            {
                for(uint k=0;k<64;k++)
                {
                    addLandRecord(i,j,k);
                }
            }
        }
    }

    function addLandRecord (uint i,uint j,uint k) private {
        landCount ++;
        candidates[landCount] = Land(i, j, k, msg.sender, 0, 0);
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