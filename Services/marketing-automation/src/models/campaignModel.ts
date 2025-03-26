import { DataTypes, Model } from 'sequelize';
import sequelize from '../config/database';

class Campaign extends Model {}

Campaign.init({
  name: { type: DataTypes.STRING, allowNull: false },
}, { sequelize });

export default Campaign;
