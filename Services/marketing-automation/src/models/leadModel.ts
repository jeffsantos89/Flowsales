import { DataTypes, Model } from 'sequelize';
import sequelize from '../config/database';

class Lead extends Model {}

Lead.init({
  email: { type: DataTypes.STRING, allowNull: false, unique: true },
}, { sequelize });

export default Lead;
