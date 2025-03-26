import { DataTypes, Model } from 'sequelize';
import sequelize from '../config/database';

class EmailLog extends Model {}

EmailLog.init({
  recipient: DataTypes.STRING,
  status: DataTypes.STRING,
}, { sequelize });

export default EmailLog;
